"""Video generation service using the Gemini Veo API.

Provides text-to-video generation for individual clips,
including polling for completion and file storage.
"""

import logging
import time
from pathlib import Path

from google.genai import types

from django.conf import settings

from core.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)

VEO_MODEL_QUALITY = "veo-3.1-generate-preview"
VEO_MODEL_FAST = "veo-3.1-fast-generate-preview"

POLL_INTERVAL_SECONDS = 10
MAX_POLL_ATTEMPTS = 360


def _get_veo_model(generation_speed):
    """Return the Veo model name based on generation speed preference.

    Args:
        generation_speed: Either "quality" or "fast".

    Returns:
        str: The Veo model identifier.
    """
    if generation_speed == "fast":
        return VEO_MODEL_FAST
    return VEO_MODEL_QUALITY


def _ensure_videos_dir():
    """Ensure the media/videos directory exists.

    Returns:
        Path: The absolute path to media/videos/.
    """
    videos_dir = Path(settings.MEDIA_ROOT) / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    return videos_dir


def _get_user_settings():
    """Load user settings, returning defaults on failure.

    Returns:
        dict: Settings with keys video_quality and generation_speed.
    """
    from core.models import UserSettings

    try:
        user_settings = UserSettings.load()
        return {
            "video_quality": user_settings.video_quality,
            "generation_speed": user_settings.generation_speed,
        }
    except Exception:
        logger.debug("UserSettings not available, using defaults.")
        return {
            "video_quality": "720p",
            "generation_speed": "quality",
        }


def _build_video_config(clip, user_settings):
    """Build the Veo API config from clip and user settings.

    Args:
        clip: A Clip model instance.
        user_settings: Dict with video_quality and generation_speed.

    Returns:
        types.GenerateVideosConfig: Configuration for the Veo API call.
    """
    project = clip.project
    resolution = user_settings["video_quality"]
    duration = project.clip_duration

    if resolution in ("1080p", "4k") and duration != 8:
        duration = 8

    return types.GenerateVideosConfig(
        aspect_ratio=project.aspect_ratio,
        resolution=resolution,
        duration_seconds=duration,
        number_of_videos=1,
        person_generation="allow_all",
    )


def _poll_operation(client, operation):
    """Poll a Veo operation until completion or failure.

    Args:
        client: The Gemini API client.
        operation: The initial operation object.

    Returns:
        The completed operation.

    Raises:
        TimeoutError: If polling exceeds MAX_POLL_ATTEMPTS.
        RuntimeError: If the operation fails.
    """
    attempts = 0
    while not operation.done:
        if attempts >= MAX_POLL_ATTEMPTS:
            raise TimeoutError(
                f"Video generation timed out after "
                f"{attempts * POLL_INTERVAL_SECONDS} seconds."
            )
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = client.operations.get(operation)
        attempts += 1

    return operation


def _build_reference_images(clip):
    """Build VideoGenerationReferenceImage list for selected references.

    Reads the clip's selected_references (list of ReferenceImage PKs),
    loads each image file, and wraps it for the Veo API.

    Args:
        clip: A Clip model instance.

    Returns:
        list: VideoGenerationReferenceImage objects, or empty list.
    """
    if not clip.selected_references:
        return []

    from core.models import ReferenceImage

    ref_images = ReferenceImage.objects.filter(
        pk__in=clip.selected_references,
        project=clip.project,
    )

    result = []
    for ref in ref_images:
        if not ref.image_file or not ref.image_file.name:
            continue
        try:
            ref_path = Path(settings.MEDIA_ROOT) / ref.image_file.name
            if not ref_path.exists():
                logger.warning("Reference image not found: %s", ref_path)
                continue

            image_bytes = ref_path.read_bytes()
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png",
            )
            result.append(
                types.VideoGenerationReferenceImage(
                    image=image_part,
                    reference_type="asset",
                )
            )
        except Exception:
            logger.warning(
                "Failed to load reference image %s for Veo.",
                ref.image_file.name,
            )

    return result


def generate_text_to_video(clip):
    """Generate a video for a clip using the Text-to-Video method.

    Calls the Veo API with the clip's script as the prompt,
    polls for completion, downloads the video file, and updates
    the clip record in the database.

    Args:
        clip: A Clip model instance with script_text populated.

    Returns:
        dict: Result data with video_url and clip_id.

    Raises:
        ValueError: If the clip has no script text.
        RuntimeError: If generation or download fails.
    """
    if not clip.script_text.strip():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no script text for video generation.")

    clip.generation_status = "generating"
    clip.save(update_fields=["generation_status"])

    try:
        client = get_ai_client()
        user_settings = _get_user_settings()
        config = _build_video_config(clip, user_settings)
        model_name = _get_veo_model(user_settings["generation_speed"])

        ref_images = _build_reference_images(clip)
        if ref_images:
            config.reference_images = ref_images

        operation = client.models.generate_videos(
            model=model_name,
            prompt=clip.script_text,
            config=config,
        )

        operation = _poll_operation(client, operation)

        generated_video = operation.response.generated_videos[0]

        videos_dir = _ensure_videos_dir()
        filename = f"clip_{clip.project.pk}_{clip.sequence_number}.mp4"
        filepath = videos_dir / filename

        client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        relative_path = f"videos/{filename}"
        clip.video_file = relative_path
        clip.generation_status = "completed"
        clip.generation_reference_id = getattr(operation, "name", "")
        clip.save(
            update_fields=[
                "video_file",
                "generation_status",
                "generation_reference_id",
            ]
        )

        logger.info(
            "Video generated for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )

        return {
            "clip_id": clip.pk,
            "video_url": f"/{settings.MEDIA_URL}{relative_path}",
        }

    except Exception as exc:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        logger.exception(
            "Video generation failed for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )
        raise RuntimeError(f"Video generation failed: {exc}") from exc


def _ensure_frames_dir():
    """Ensure the media/images/frames directory exists.

    Returns:
        Path: The absolute path to media/images/frames/.
    """
    frames_dir = Path(settings.MEDIA_ROOT) / "images" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    return frames_dir


def generate_first_frame_image(clip):
    """Generate a first-frame image for a clip using the Gemini image API.

    Creates an image from the clip's script suitable for use as
    a starting frame in Image-to-Video generation.

    Args:
        clip: A Clip model instance with script_text populated.

    Returns:
        str: Relative file path to the generated frame image.

    Raises:
        ValueError: If the clip has no script text.
        RuntimeError: If image generation fails.
    """
    if not clip.script_text.strip():
        raise ValueError("Clip has no script text for frame generation.")

    from core.services.image_generator import (
        IMAGE_MODEL,
        _extract_image_part,
    )

    client = get_ai_client()
    prompt = (
        f"Generate a cinematic still frame for the opening moment "
        f"of this video clip: {clip.script_text}"
    )

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            image_size="1K",
            aspect_ratio=clip.project.aspect_ratio.replace(":", ":"),
        ),
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=config,
    )

    image_part = _extract_image_part(response)

    frames_dir = _ensure_frames_dir()
    filename = f"first_{clip.project.pk}_{clip.sequence_number}.png"
    filepath = frames_dir / filename

    filepath.write_bytes(image_part.inline_data.data)

    relative_path = f"images/frames/{filename}"
    clip.first_frame = relative_path
    clip.save(update_fields=["first_frame"])

    logger.info(
        "First frame generated for Clip %s of Project '%s'.",
        clip.sequence_number,
        clip.project.title,
    )
    return relative_path


def generate_image_to_video(clip):
    """Generate a video for a clip using the Image-to-Video method.

    Calls the Veo API with the clip's first_frame image as the
    starting frame and the clip's script as the prompt.

    Args:
        clip: A Clip model instance with first_frame and script_text set.

    Returns:
        dict: Result data with video_url and clip_id.

    Raises:
        ValueError: If the clip has no first frame or no script text.
        RuntimeError: If generation or download fails.
    """
    if not clip.script_text.strip():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no script text for video generation.")

    if not clip.first_frame or not clip.first_frame.name:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no first frame set for Image-to-Video.")

    first_frame_path = Path(settings.MEDIA_ROOT) / clip.first_frame.name
    if not first_frame_path.exists():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError(f"First frame file not found: {clip.first_frame.name}")

    clip.generation_status = "generating"
    clip.save(update_fields=["generation_status"])

    try:
        client = get_ai_client()
        user_settings = _get_user_settings()
        config = _build_video_config(clip, user_settings)
        model_name = _get_veo_model(user_settings["generation_speed"])

        ref_images = _build_reference_images(clip)
        if ref_images:
            config.reference_images = ref_images

        image_bytes = first_frame_path.read_bytes()
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",
        )

        operation = client.models.generate_videos(
            model=model_name,
            prompt=clip.script_text,
            image=image_part,
            config=config,
        )

        operation = _poll_operation(client, operation)

        generated_video = operation.response.generated_videos[0]

        videos_dir = _ensure_videos_dir()
        filename = f"clip_{clip.project.pk}_{clip.sequence_number}.mp4"
        filepath = videos_dir / filename

        client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        relative_path = f"videos/{filename}"
        clip.video_file = relative_path
        clip.generation_status = "completed"
        clip.generation_reference_id = getattr(operation, "name", "")
        clip.save(
            update_fields=[
                "video_file",
                "generation_status",
                "generation_reference_id",
            ]
        )

        logger.info(
            "Image-to-Video generated for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )

        return {
            "clip_id": clip.pk,
            "video_url": f"/{settings.MEDIA_URL}{relative_path}",
        }

    except Exception as exc:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        logger.exception(
            "Image-to-Video failed for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )
        raise RuntimeError(f"Image-to-Video generation failed: {exc}") from exc


def generate_last_frame_image(clip):
    """Generate a last-frame image for a clip using the Gemini image API.

    Creates an image from the clip's script suitable for use as
    an ending frame in Frame Interpolation generation.

    Args:
        clip: A Clip model instance with script_text populated.

    Returns:
        str: Relative file path to the generated frame image.

    Raises:
        ValueError: If the clip has no script text.
        RuntimeError: If image generation fails.
    """
    if not clip.script_text.strip():
        raise ValueError("Clip has no script text for frame generation.")

    from core.services.image_generator import (
        IMAGE_MODEL,
        _extract_image_part,
    )

    client = get_ai_client()
    prompt = (
        f"Generate a cinematic still frame for the closing moment "
        f"of this video clip: {clip.script_text}"
    )

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            image_size="1K",
            aspect_ratio=clip.project.aspect_ratio.replace(":", ":"),
        ),
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=config,
    )

    image_part = _extract_image_part(response)

    frames_dir = _ensure_frames_dir()
    filename = f"last_{clip.project.pk}_{clip.sequence_number}.png"
    filepath = frames_dir / filename

    filepath.write_bytes(image_part.inline_data.data)

    relative_path = f"images/frames/{filename}"
    clip.last_frame = relative_path
    clip.save(update_fields=["last_frame"])

    logger.info(
        "Last frame generated for Clip %s of Project '%s'.",
        clip.sequence_number,
        clip.project.title,
    )
    return relative_path


def generate_frame_interpolation(clip):
    """Generate a video using Frame Interpolation between first and last frames.

    Calls the Veo API with both the first_frame and last_frame images
    and the clip's script as the prompt. The generated video starts
    at the first frame and ends at the last frame.

    Args:
        clip: A Clip model instance with first_frame, last_frame,
              and script_text set.

    Returns:
        dict: Result data with video_url and clip_id.

    Raises:
        ValueError: If the clip lacks script, first frame, or last frame.
        RuntimeError: If generation or download fails.
    """
    if not clip.script_text.strip():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no script text for video generation.")

    if not clip.first_frame or not clip.first_frame.name:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no first frame set for Frame Interpolation.")

    if not clip.last_frame or not clip.last_frame.name:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no last frame set for Frame Interpolation.")

    first_frame_path = Path(settings.MEDIA_ROOT) / clip.first_frame.name
    if not first_frame_path.exists():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError(f"First frame file not found: {clip.first_frame.name}")

    last_frame_path = Path(settings.MEDIA_ROOT) / clip.last_frame.name
    if not last_frame_path.exists():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError(f"Last frame file not found: {clip.last_frame.name}")

    clip.generation_status = "generating"
    clip.save(update_fields=["generation_status"])

    try:
        client = get_ai_client()
        user_settings = _get_user_settings()
        config = _build_video_config(clip, user_settings)
        model_name = _get_veo_model(user_settings["generation_speed"])

        ref_images = _build_reference_images(clip)
        if ref_images:
            config.reference_images = ref_images

        first_bytes = first_frame_path.read_bytes()
        first_image = types.Part.from_bytes(
            data=first_bytes,
            mime_type="image/png",
        )

        last_bytes = last_frame_path.read_bytes()
        last_image = types.Part.from_bytes(
            data=last_bytes,
            mime_type="image/png",
        )

        operation = client.models.generate_videos(
            model=model_name,
            prompt=clip.script_text,
            image=first_image,
            config=config,
            end_image=last_image,
        )

        operation = _poll_operation(client, operation)

        generated_video = operation.response.generated_videos[0]

        videos_dir = _ensure_videos_dir()
        filename = f"clip_{clip.project.pk}_{clip.sequence_number}.mp4"
        filepath = videos_dir / filename

        client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        relative_path = f"videos/{filename}"
        clip.video_file = relative_path
        clip.generation_status = "completed"
        clip.generation_reference_id = getattr(operation, "name", "")
        clip.save(
            update_fields=[
                "video_file",
                "generation_status",
                "generation_reference_id",
            ]
        )

        logger.info(
            "Frame Interpolation generated for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )

        return {
            "clip_id": clip.pk,
            "video_url": f"/{settings.MEDIA_URL}{relative_path}",
        }

    except Exception as exc:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        logger.exception(
            "Frame Interpolation failed for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )
        raise RuntimeError(f"Frame Interpolation generation failed: {exc}") from exc


def generate_extend_from_previous(clip):
    """Generate a video by extending the previous clip's video.

    Uses the Veo Extension API to continue the previous clip's
    video with the current clip's script as the extension prompt.
    The result is a combined video that is split: the previous
    clip keeps its original portion, and the new portion becomes
    the current clip's video. Resolution is locked to 720p.

    Args:
        clip: A Clip model instance (must be Clip 2 or higher).

    Returns:
        dict: Result data with video_url and clip_id.

    Raises:
        ValueError: If the clip is Clip 1 or previous clip lacks a video.
        RuntimeError: If generation or download fails.
    """
    if clip.sequence_number <= 1:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Extend from Previous Clip is not available for Clip 1.")

    from core.models import Clip as ClipModel

    previous_clip = ClipModel.objects.filter(
        project=clip.project,
        sequence_number=clip.sequence_number - 1,
    ).first()

    if not previous_clip:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Previous clip not found.")

    if not previous_clip.video_file or not previous_clip.video_file.name:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Previous clip has no generated video.")

    if not previous_clip.generation_reference_id:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError(
            "Previous clip has no generation reference ID. "
            "Regenerate the previous clip's video first."
        )

    if not clip.script_text.strip():
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        raise ValueError("Clip has no script text for video generation.")

    clip.generation_status = "generating"
    clip.save(update_fields=["generation_status"])

    try:
        client = get_ai_client()

        operation = client.models.generate_videos(
            model=VEO_MODEL_QUALITY,
            prompt=clip.script_text.strip(),
            video=types.Video(
                uri=previous_clip.generation_reference_id,
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                resolution="720p",
                person_generation="allow_all",
            ),
        )

        operation = _poll_operation(client, operation)

        generated_video = operation.response.generated_videos[0]

        videos_dir = _ensure_videos_dir()
        filename = f"clip_{clip.project.pk}_{clip.sequence_number}" f"_from_prev.mp4"
        filepath = videos_dir / filename

        client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        relative_path = f"videos/{filename}"
        clip.video_file = relative_path
        clip.generation_status = "completed"
        clip.generation_reference_id = getattr(operation, "name", "")
        clip.save(
            update_fields=[
                "video_file",
                "generation_status",
                "generation_reference_id",
            ]
        )

        logger.info(
            "Extend from Previous generated for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )

        return {
            "clip_id": clip.pk,
            "video_url": f"/{settings.MEDIA_URL}{relative_path}",
        }

    except Exception as exc:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        logger.exception(
            "Extend from Previous failed for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )
        raise RuntimeError(f"Extend from Previous generation failed: {exc}") from exc
