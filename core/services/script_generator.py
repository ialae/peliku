"""AI-powered script generation for video clips.

Uses the Gemini API to generate, regenerate, and refine
video production scripts for reel projects.
"""

import json
import logging

from google.genai import types

from core.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3-flash-preview"

SYSTEM_PROMPT = (
    "You are a professional video production scriptwriter. "
    "You write detailed, production-ready scripts for short-form video reels. "
    "Each script is a prompt that will be fed to an AI video generator, "
    "so it must include: subject, action, camera motion, composition, "
    "lighting, color palette, ambient sounds, dialogue (in quotes), "
    "and how the clip connects to the previous and next clips.\n\n"
    "All scripts in a reel share a unified narrative thread (fil conducteur), "
    "recurring visual motifs, consistent character descriptions, "
    "and a unified color palette. Scripts include audio cues "
    "(dialogue in quotes, sound effects described explicitly, "
    "ambient noise specified) so the AI video generator produces "
    "appropriate sound.\n\n"
    "The first clip's script establishes the scene. "
    "The last clip's script provides a clear resolution or punchline."
)

GENERATE_ALL_PROMPT_TEMPLATE = (
    "Write {num_clips} video clip scripts for this reel:\n\n"
    "Title: {title}\n"
    "Description: {description}\n"
    "Aspect Ratio: {aspect_ratio}\n"
    "Clip Duration: {clip_duration} seconds each\n"
    "{visual_style_line}"
    "\nReturn a JSON array of exactly {num_clips} strings, "
    "where each string is one clip script. "
    "Do not include any other text outside the JSON array."
)

REGENERATE_SINGLE_PROMPT_TEMPLATE = (
    "Rewrite the script for Clip {clip_number} of a {num_clips}-clip reel.\n\n"
    "Title: {title}\n"
    "Description: {description}\n"
    "Aspect Ratio: {aspect_ratio}\n"
    "Clip Duration: {clip_duration} seconds\n"
    "{visual_style_line}"
    "{previous_clip_line}"
    "{next_clip_line}"
    "\nThe rewritten script must maintain narrative flow with "
    "the neighboring clips, preserve the global visual style, "
    "characters, and mood.\n\n"
    "Return only the new script text as a plain string. "
    "Do not wrap it in JSON or add any other text."
)

REGENERATE_ALL_PROMPT_TEMPLATE = (
    "Rewrite all {num_clips} clip scripts from scratch "
    "for this reel:\n\n"
    "Title: {title}\n"
    "Description: {description}\n"
    "Aspect Ratio: {aspect_ratio}\n"
    "Clip Duration: {clip_duration} seconds each\n"
    "{visual_style_line}"
    "\nReturn a JSON array of exactly {num_clips} strings, "
    "where each string is one clip script. "
    "Do not include any other text outside the JSON array."
)


def _build_visual_style_line(visual_style):
    """Build the visual style line for prompts."""
    if visual_style:
        return f"Visual Style: {visual_style}\n"
    return ""


def _parse_script_list(response_text, expected_count):
    """Parse a JSON array of scripts from the API response.

    Args:
        response_text: Raw text response from the Gemini API.
        expected_count: Expected number of scripts in the array.

    Returns:
        list[str]: Parsed list of script strings.

    Raises:
        ValueError: If parsing fails or count does not match.
    """
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines) - 1
        if lines[0].startswith("```json"):
            start = 1
        if lines[-1].strip() == "```":
            end = len(lines) - 1
        text = "\n".join(lines[start:end])

    scripts = json.loads(text)
    if not isinstance(scripts, list):
        raise ValueError("Expected a JSON array of scripts")
    if len(scripts) != expected_count:
        raise ValueError(f"Expected {expected_count} scripts, got {len(scripts)}")
    return [str(s) for s in scripts]


def generate_all_scripts(project):
    """Generate scripts for all clips in a project.

    Calls the Gemini API to produce one script per clip,
    sharing a unified narrative thread.

    Args:
        project: A Project model instance with title, description,
            visual_style, aspect_ratio, clip_duration, and num_clips.

    Returns:
        list[str]: A list of script strings, one per clip.

    Raises:
        ValueError: If the API response cannot be parsed.
        Exception: If the API call fails.
    """
    client = get_ai_client()
    prompt = GENERATE_ALL_PROMPT_TEMPLATE.format(
        num_clips=project.num_clips,
        title=project.title,
        description=project.description,
        aspect_ratio=project.aspect_ratio,
        clip_duration=project.clip_duration,
        visual_style_line=_build_visual_style_line(project.visual_style),
    )

    logger.info(
        "Generating %d scripts for project '%s'",
        project.num_clips,
        project.title,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    scripts = _parse_script_list(response.text, project.num_clips)
    logger.info(
        "Generated %d scripts for project '%s'",
        len(scripts),
        project.title,
    )
    return scripts


def regenerate_single_script(clip):
    """Regenerate the script for a single clip using neighbor context.

    Rewrites one clip's script while maintaining coherence with
    the clips before and after it.

    Args:
        clip: A Clip model instance with project, sequence_number,
            and script_text populated.

    Returns:
        str: The new script text for the clip.

    Raises:
        Exception: If the API call fails.
    """
    client = get_ai_client()
    project = clip.project
    clips = list(project.clips.order_by("sequence_number"))
    clip_index = next(i for i, c in enumerate(clips) if c.pk == clip.pk)

    previous_script = ""
    if clip_index > 0:
        previous_script = clips[clip_index - 1].script_text

    next_script = ""
    if clip_index < len(clips) - 1:
        next_script = clips[clip_index + 1].script_text

    previous_clip_line = ""
    if previous_script:
        previous_clip_line = (
            f"Previous clip script (Clip {clip.sequence_number - 1}):\n"
            f"{previous_script}\n\n"
        )

    next_clip_line = ""
    if next_script:
        next_clip_line = (
            f"Next clip script (Clip {clip.sequence_number + 1}):\n"
            f"{next_script}\n\n"
        )

    prompt = REGENERATE_SINGLE_PROMPT_TEMPLATE.format(
        clip_number=clip.sequence_number,
        num_clips=len(clips),
        title=project.title,
        description=project.description,
        aspect_ratio=project.aspect_ratio,
        clip_duration=project.clip_duration,
        visual_style_line=_build_visual_style_line(project.visual_style),
        previous_clip_line=previous_clip_line,
        next_clip_line=next_clip_line,
    )

    logger.info(
        "Regenerating script for clip %d of project '%s'",
        clip.sequence_number,
        project.title,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    script = response.text.strip()
    logger.info(
        "Regenerated script for clip %d of project '%s'",
        clip.sequence_number,
        project.title,
    )
    return script


def regenerate_all_scripts(project):
    """Regenerate all clip scripts from scratch.

    Rewrites every script based on the current project metadata.

    Args:
        project: A Project model instance.

    Returns:
        list[str]: A list of new script strings, one per clip.

    Raises:
        ValueError: If the API response cannot be parsed.
        Exception: If the API call fails.
    """
    client = get_ai_client()
    num_clips = project.clips.count()
    prompt = REGENERATE_ALL_PROMPT_TEMPLATE.format(
        num_clips=num_clips,
        title=project.title,
        description=project.description,
        aspect_ratio=project.aspect_ratio,
        clip_duration=project.clip_duration,
        visual_style_line=_build_visual_style_line(project.visual_style),
    )

    logger.info(
        "Regenerating all %d scripts for project '%s'",
        num_clips,
        project.title,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    scripts = _parse_script_list(response.text, num_clips)
    logger.info(
        "Regenerated %d scripts for project '%s'",
        len(scripts),
        project.title,
    )
    return scripts
