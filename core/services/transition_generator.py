"""Transition frame generation service using the Gemini image API.

Generates a pair of transition frames (ending frame for clip N,
starting frame for clip N+1) to enable smooth visual continuity
between consecutive clips via frame interpolation.
"""

import logging
from pathlib import Path

from google.genai import types

from django.conf import settings

from core.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)

IMAGE_MODEL = "gemini-3.1-flash-image-preview"
IMAGE_SIZE = "1K"
TRANSITION_IMAGE_ASPECT_RATIO = "9:16"


def _ensure_frames_dir():
    """Ensure the media/images/frames directory exists.

    Returns:
        Path: The absolute path to media/images/frames/.
    """
    frames_dir = Path(settings.MEDIA_ROOT) / "images" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    return frames_dir


def _build_ending_frame_prompt(clip_above, clip_below):
    """Build the prompt for generating the ending frame of the upper clip.

    Args:
        clip_above: The Clip instance whose ending frame we generate.
        clip_below: The next Clip instance for narrative context.

    Returns:
        str: The generation prompt.
    """
    return (
        "Generate a single photorealistic still image representing the "
        "ideal ending frame of the following video clip. This frame must "
        "visually bridge toward the next clip's content.\n\n"
        f"CURRENT CLIP SCRIPT (ending):\n{clip_above.script_text}\n\n"
        f"NEXT CLIP SCRIPT (beginning):\n{clip_below.script_text}\n\n"
        "The image should capture the final visual moment of the current "
        "clip that naturally leads into the next clip's opening."
    )


def _build_starting_frame_prompt(clip_above, clip_below):
    """Build the prompt for generating the starting frame of the lower clip.

    Args:
        clip_above: The previous Clip instance for narrative context.
        clip_below: The Clip instance whose starting frame we generate.

    Returns:
        str: The generation prompt.
    """
    return (
        "Generate a single photorealistic still image representing the "
        "ideal starting frame of the following video clip. This frame must "
        "visually connect back to the previous clip's conclusion.\n\n"
        f"PREVIOUS CLIP SCRIPT (ending):\n{clip_above.script_text}\n\n"
        f"CURRENT CLIP SCRIPT (beginning):\n{clip_below.script_text}\n\n"
        "The image should capture the opening visual moment of the current "
        "clip that flows naturally from the previous clip's ending."
    )


def _generate_image(prompt):
    """Call the Gemini image API and return the raw image bytes.

    Args:
        prompt: The text prompt for image generation.

    Returns:
        bytes: The generated image data.

    Raises:
        RuntimeError: If generation fails or returns no image.
    """
    client = get_ai_client()

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            image_size=IMAGE_SIZE,
            aspect_ratio=TRANSITION_IMAGE_ASPECT_RATIO,
        ),
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=config,
    )

    if not response.candidates:
        raise RuntimeError("Transition frame generation returned no candidates.")

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part.inline_data.data

    raise RuntimeError("Transition frame generation returned no image data.")


def generate_transition_frames(clip_above, clip_below):
    """Generate transition frames for two consecutive clips.

    Creates an ending frame for *clip_above* and a starting frame for
    *clip_below* using AI image generation, saves both to disk, and
    updates the clip model fields.

    Args:
        clip_above: The upper Clip instance (gets its last_frame set).
        clip_below: The lower Clip instance (gets its first_frame set).

    Returns:
        dict: A dictionary with ``last_frame_path`` and
            ``first_frame_path`` relative to MEDIA_ROOT.

    Raises:
        RuntimeError: If either image generation call fails.
    """
    frames_dir = _ensure_frames_dir()

    ending_prompt = _build_ending_frame_prompt(clip_above, clip_below)
    ending_bytes = _generate_image(ending_prompt)

    ending_filename = f"transition_{clip_above.project_id}" f"_{clip_above.pk}_last.png"
    ending_path = frames_dir / ending_filename
    ending_path.write_bytes(ending_bytes)
    last_frame_relative = f"images/frames/{ending_filename}"

    starting_prompt = _build_starting_frame_prompt(clip_above, clip_below)
    starting_bytes = _generate_image(starting_prompt)

    starting_filename = (
        f"transition_{clip_below.project_id}" f"_{clip_below.pk}_first.png"
    )
    starting_path = frames_dir / starting_filename
    starting_path.write_bytes(starting_bytes)
    first_frame_relative = f"images/frames/{starting_filename}"

    clip_above.last_frame = last_frame_relative
    clip_above.save(update_fields=["last_frame"])

    clip_below.first_frame = first_frame_relative
    clip_below.save(update_fields=["first_frame"])

    logger.info(
        "Transition frames generated between clip %d and clip %d.",
        clip_above.pk,
        clip_below.pk,
    )

    return {
        "last_frame_path": last_frame_relative,
        "first_frame_path": first_frame_relative,
    }
