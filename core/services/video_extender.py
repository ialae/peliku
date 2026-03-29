"""Video extension service using the Veo Video Extension API.

Extends an existing clip's video by 7 seconds using a user-provided
extension prompt. Resolution is locked to 720p per Veo constraints.
"""

import logging
import time
from pathlib import Path

from google.genai import types

from django.conf import settings

from core.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)

VEO_MODEL = "veo-3.1-generate-preview"
POLL_INTERVAL_SECONDS = 10
MAX_POLL_ATTEMPTS = 360
MAX_EXTENSIONS = 20


def _ensure_videos_dir():
    """Ensure the media/videos directory exists.

    Returns:
        Path: The absolute path to media/videos/.
    """
    videos_dir = Path(settings.MEDIA_ROOT) / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    return videos_dir


def _poll_operation(client, operation):
    """Poll a Veo operation until completion or failure.

    Args:
        client: The Gemini API client.
        operation: The initial operation object.

    Returns:
        The completed operation.

    Raises:
        TimeoutError: If polling exceeds MAX_POLL_ATTEMPTS.
    """
    attempts = 0
    while not operation.done:
        if attempts >= MAX_POLL_ATTEMPTS:
            raise TimeoutError(
                f"Video extension timed out after "
                f"{attempts * POLL_INTERVAL_SECONDS} seconds."
            )
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = client.operations.get(operation)
        attempts += 1

    return operation


def extend_clip_video(clip, extension_prompt):
    """Extend a clip's video by 7 seconds using the Veo Extension API.

    Calls the Veo API with the clip's generation_reference_id and the
    extension prompt. Downloads the extended video, replaces the clip's
    video_file, and increments extension_count.

    Args:
        clip: A Clip model instance with a completed video.
        extension_prompt: A string describing what happens next.

    Returns:
        dict: Result data with video_url and clip_id.

    Raises:
        ValueError: If preconditions are not met.
        RuntimeError: If extension fails.
    """
    if not clip.video_file or not clip.video_file.name:
        raise ValueError("Clip has no generated video to extend.")

    if not clip.generation_reference_id:
        raise ValueError(
            "Clip has no generation reference ID. "
            "Video must be generated in the current session."
        )

    if clip.extension_count >= MAX_EXTENSIONS:
        raise ValueError(
            f"Maximum extension limit reached ({MAX_EXTENSIONS}). "
            f"Cannot extend further."
        )

    if not extension_prompt or not extension_prompt.strip():
        raise ValueError("Extension prompt is required.")

    clip.generation_status = "generating"
    clip.save(update_fields=["generation_status"])

    try:
        client = get_ai_client()

        operation = client.models.generate_videos(
            model=VEO_MODEL,
            prompt=extension_prompt.strip(),
            video=types.Video(
                uri=clip.generation_reference_id,
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
        ext_num = clip.extension_count + 1
        filename = f"clip_{clip.project.pk}_{clip.sequence_number}" f"_ext{ext_num}.mp4"
        filepath = videos_dir / filename

        client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        relative_path = f"videos/{filename}"
        clip.video_file = relative_path
        clip.generation_status = "completed"
        clip.extension_count = ext_num
        clip.generation_reference_id = getattr(operation, "name", "")
        clip.save(
            update_fields=[
                "video_file",
                "generation_status",
                "extension_count",
                "generation_reference_id",
            ]
        )

        logger.info(
            "Video extended for Clip %s of Project '%s' (extension %d).",
            clip.sequence_number,
            clip.project.title,
            ext_num,
        )

        return {
            "clip_id": clip.pk,
            "video_url": f"/{settings.MEDIA_URL}{relative_path}",
            "extension_count": ext_num,
        }

    except Exception as exc:
        clip.generation_status = "failed"
        clip.save(update_fields=["generation_status"])
        logger.exception(
            "Video extension failed for Clip %s of Project '%s'.",
            clip.sequence_number,
            clip.project.title,
        )
        raise RuntimeError(f"Video extension failed: {exc}") from exc
