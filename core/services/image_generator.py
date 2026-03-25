"""Reference image generation service using the Gemini Nano Banana API.

Generates reference images for visual consistency across video clips.
Uses the Nano Banana 2 (Gemini 3.1 Flash Image) model for speed.
"""

import logging
from pathlib import Path

from google.genai import types

from django.conf import settings

from core.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)

IMAGE_MODEL = "gemini-3.1-flash-image-preview"
IMAGE_SIZE = "1K"
IMAGE_ASPECT_RATIO = "1:1"


def _ensure_references_dir():
    """Ensure the media/images/references directory exists.

    Returns:
        Path: The absolute path to media/images/references/.
    """
    refs_dir = Path(settings.MEDIA_ROOT) / "images" / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    return refs_dir


def generate_reference_image(prompt, project_id, slot_number):
    """Generate a reference image via Gemini Nano Banana API.

    Calls the image generation model with the given prompt,
    saves the resulting image to media/images/references/,
    and returns the relative file path.

    Args:
        prompt: Text description of the image to generate.
        project_id: The project PK (used in the filename).
        slot_number: The reference slot number (1-3).

    Returns:
        str: Relative file path (e.g. "images/references/ref_1_2.png").

    Raises:
        RuntimeError: If generation fails or produces no image.
    """
    client = get_ai_client()

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            image_size=IMAGE_SIZE,
            aspect_ratio=IMAGE_ASPECT_RATIO,
        ),
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=config,
    )

    image_part = _extract_image_part(response)

    refs_dir = _ensure_references_dir()
    filename = f"ref_{project_id}_{slot_number}.png"
    filepath = refs_dir / filename

    filepath.write_bytes(image_part.inline_data.data)

    relative_path = f"images/references/{filename}"
    logger.info(
        "Reference image generated for project %s, slot %s.",
        project_id,
        slot_number,
    )
    return relative_path


def _extract_image_part(response):
    """Extract the first image part from a Gemini response.

    Args:
        response: The Gemini API response object.

    Returns:
        The image part containing inline_data.

    Raises:
        RuntimeError: If no image was found in the response.
    """
    if not response.candidates:
        raise RuntimeError("Image generation returned no candidates.")

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part

    raise RuntimeError("Image generation returned no image data.")
