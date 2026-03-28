"""Views for the core app."""

import json
import logging

from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.forms import ProjectForm
from core.models import Clip, Project, ReferenceImage, Task, UserSettings
from core.services.image_generator import generate_reference_image
from core.services.script_generator import (
    generate_all_scripts,
    regenerate_all_scripts,
    regenerate_single_script,
)
from core.services.task_runner import run_in_background
from core.services.video_generator import (
    generate_first_frame_image,
    generate_frame_interpolation,
    generate_image_to_video,
    generate_last_frame_image,
    generate_text_to_video,
)

logger = logging.getLogger(__name__)


def home(request):
    """Render the home page with real projects from the database."""
    projects = Project.objects.all().order_by("-updated_at")
    project_data = []
    for project in projects:
        total_clips = project.clips.count()
        generated_clips = project.clips.filter(generation_status="completed").count()
        project_data.append(
            {
                "project": project,
                "total_clips": total_clips,
                "generated_clips": generated_clips,
            }
        )
    context = {
        "project_data": project_data,
    }
    return render(request, "core/home.html", context)


def project_form(request):
    """Render the new-project form or handle POST to create a project."""
    if request.method == "POST":
        return _handle_create_project(request)

    defaults = {
        "aspect_ratio": "9:16",
        "clip_duration": 8,
        "num_clips": 7,
        "visual_style": "",
    }
    try:
        settings = UserSettings.load()
        defaults = {
            "aspect_ratio": settings.default_aspect_ratio,
            "clip_duration": settings.default_clip_duration,
            "num_clips": settings.default_num_clips,
            "visual_style": settings.default_visual_style,
        }
    except Exception:
        logger.debug("UserSettings not available, using form defaults.")

    return render(request, "core/project_form.html", {"defaults": defaults})


def _handle_create_project(request):
    """Validate form data, create project with AI scripts, redirect."""
    form = ProjectForm(request.POST)
    if not form.is_valid():
        errors = {field: error_list[0] for field, error_list in form.errors.items()}
        return render(
            request,
            "core/project_form.html",
            {
                "errors": errors,
                "form_data": request.POST,
                "defaults": {
                    "aspect_ratio": "",
                    "clip_duration": "",
                    "num_clips": "",
                    "visual_style": "",
                },
            },
        )

    project = Project.objects.create(
        title=form.cleaned_data["title"],
        description=form.cleaned_data["description"],
        visual_style=form.cleaned_data["visual_style"],
        aspect_ratio=form.cleaned_data["aspect_ratio"],
        clip_duration=form.cleaned_data["clip_duration"],
        num_clips=form.cleaned_data["num_clips"],
    )

    scripts = _generate_scripts_safely(project)
    num_clips = form.cleaned_data["num_clips"]

    for seq in range(1, num_clips + 1):
        script_text = scripts[seq - 1] if scripts else ""
        Clip.objects.create(
            project=project,
            sequence_number=seq,
            script_text=script_text,
        )

    return redirect("core:workspace", project_id=project.pk)


def _generate_scripts_safely(project):
    """Call AI script generation, returning empty list on failure.

    Args:
        project: A Project model instance.

    Returns:
        list[str]: Generated scripts, or empty list if generation fails.
    """
    try:
        return generate_all_scripts(project)
    except Exception:
        logger.warning(
            "AI script generation failed for project '%s'; "
            "clips will have empty scripts.",
            project.title,
            exc_info=True,
        )
        return []


def workspace(request, project_id):
    """Render the Project Workspace page with real project data."""
    project = get_object_or_404(Project, pk=project_id)
    clips = project.clips.all().order_by("sequence_number")
    references = project.reference_images.all().order_by("slot_number")

    context = {
        "project": project,
        "clips": clips,
        "references": references,
    }
    return render(request, "core/workspace.html", context)


@csrf_exempt
@require_POST
def api_delete_project(request, project_id):
    """Delete a project and all associated media files."""
    project = get_object_or_404(Project, pk=project_id)

    _delete_project_media(project)
    project.delete()

    return JsonResponse({"status": "deleted"})


def _delete_project_media(project):
    """Remove media files from disk for a project's clips and references."""
    for clip in project.clips.all():
        if clip.video_file and clip.video_file.name:
            try:
                clip.video_file.delete(save=False)
            except Exception:
                logger.warning("Failed to delete video: %s", clip.video_file.name)
        if clip.first_frame and clip.first_frame.name:
            try:
                clip.first_frame.delete(save=False)
            except Exception:
                logger.warning("Failed to delete frame: %s", clip.first_frame.name)
        if clip.last_frame and clip.last_frame.name:
            try:
                clip.last_frame.delete(save=False)
            except Exception:
                logger.warning("Failed to delete frame: %s", clip.last_frame.name)

    for ref in project.reference_images.all():
        if ref.image_file and ref.image_file.name:
            try:
                ref.image_file.delete(save=False)
            except Exception:
                logger.warning("Failed to delete ref image: %s", ref.image_file.name)


@csrf_exempt
@require_POST
def api_rename_project(request, project_id):
    """Rename a project. Accepts JSON {"title": "New Name"}."""
    project = get_object_or_404(Project, pk=project_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    new_title = body.get("title", "").strip()
    if not new_title:
        return JsonResponse({"error": "Title is required."}, status=400)
    if len(new_title) > 100:
        return JsonResponse(
            {"error": "Title must be 100 characters or fewer."}, status=400
        )

    project.title = new_title
    project.save(update_fields=["title", "updated_at"])

    return JsonResponse({"status": "renamed", "title": project.title})


@csrf_exempt
@require_POST
def api_duplicate_project(request, project_id):
    """Duplicate a project: copies metadata, clips scripts, refs. No videos."""
    project = get_object_or_404(Project, pk=project_id)

    new_project = Project.objects.create(
        title=f"{project.title} (Copy)",
        description=project.description,
        visual_style=project.visual_style,
        aspect_ratio=project.aspect_ratio,
        clip_duration=project.clip_duration,
        num_clips=project.num_clips,
    )

    for clip in project.clips.all():
        Clip.objects.create(
            project=new_project,
            sequence_number=clip.sequence_number,
            script_text=clip.script_text,
        )

    for ref in project.reference_images.all():
        new_file_name = ""
        if ref.image_file and ref.image_file.name:
            try:
                from django.core.files.base import ContentFile

                original_file = ref.image_file
                original_file.open("rb")
                content = original_file.read()
                original_file.close()
                new_ref = ReferenceImage(
                    project=new_project,
                    slot_number=ref.slot_number,
                    label=ref.label,
                )
                new_ref.image_file.save(
                    original_file.name.split("/")[-1],
                    ContentFile(content),
                    save=True,
                )
                continue
            except Exception:
                logger.warning("Failed to copy ref image: %s", ref.image_file.name)
                new_file_name = ref.image_file.name

        ReferenceImage.objects.create(
            project=new_project,
            slot_number=ref.slot_number,
            image_file=new_file_name or ref.image_file.name,
            label=ref.label,
        )

    return JsonResponse(
        {
            "status": "duplicated",
            "new_project_id": new_project.pk,
            "new_title": new_project.title,
        }
    )


MAX_SCRIPT_LENGTH = 2000


@csrf_exempt
@require_POST
def api_update_clip_script(request, clip_id):
    """Update a clip's script text. Accepts JSON {"script_text": "..."}."""
    clip = get_object_or_404(Clip, pk=clip_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    script_text = body.get("script_text")
    if script_text is None:
        return JsonResponse({"error": "script_text is required."}, status=400)

    if not isinstance(script_text, str):
        return JsonResponse({"error": "script_text must be a string."}, status=400)

    if len(script_text) > MAX_SCRIPT_LENGTH:
        return JsonResponse(
            {
                "error": f"Script must be {MAX_SCRIPT_LENGTH} characters or fewer.",
            },
            status=400,
        )

    clip.script_text = script_text
    clip.save(update_fields=["script_text"])

    return JsonResponse({"status": "updated", "clip_id": clip.pk})


VALID_METHODS = {
    "text_to_video",
    "image_to_video",
    "frame_interpolation",
    "extend_previous",
}


@csrf_exempt
@require_POST
def api_update_generation_method(request, clip_id):
    """Update a clip's generation method.

    POST /api/clips/<id>/update-method/
    Body JSON: {"method": "image_to_video"}
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    method = body.get("method", "").strip()
    if method not in VALID_METHODS:
        return JsonResponse(
            {"error": f"method must be one of: {', '.join(sorted(VALID_METHODS))}."},
            status=400,
        )

    clip.generation_method = method
    clip.save(update_fields=["generation_method"])

    return JsonResponse({"status": "updated", "clip_id": clip.pk, "method": method})


def api_task_status(request, task_id):
    """Return the current status of a background task as JSON.

    GET /api/tasks/<id>/status/

    Response JSON:
        {
            "id": <int>,
            "task_type": <str>,
            "status": "pending" | "running" | "completed" | "failed",
            "progress": <int 0-100>,
            "result_data": <dict|list|null>,
            "error_message": <str>
        }
    """
    task = get_object_or_404(Task, pk=task_id)

    return JsonResponse(
        {
            "id": task.pk,
            "task_type": task.task_type,
            "status": task.status,
            "progress": task.progress,
            "result_data": task.result_data,
            "error_message": task.error_message,
        }
    )


@csrf_exempt
@require_POST
def api_generate_video(request, clip_id):
    """Start background video generation for a clip.

    POST /api/clips/<id>/generate-video/

    Dispatches to the appropriate generator based on clip.generation_method.
    Accepts optional JSON body {"method": "text_to_video"} to override.

    Returns JSON {"task_id": <int>} with HTTP 202 on success.
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    if clip.generation_status == "generating":
        return JsonResponse(
            {"error": "Video generation is already in progress."},
            status=409,
        )

    if not clip.script_text.strip():
        return JsonResponse(
            {"error": "Clip has no script text. Write a script first."},
            status=400,
        )

    method = clip.generation_method
    try:
        body = json.loads(request.body) if request.body else {}
        if "method" in body:
            method = body["method"]
    except (json.JSONDecodeError, ValueError):
        pass

    generator_func = _get_generator_for_method(method)
    if generator_func is None:
        return JsonResponse(
            {"error": f"Unknown generation method: {method}"},
            status=400,
        )

    if method == "image_to_video":
        if not clip.first_frame or not clip.first_frame.name:
            return JsonResponse(
                {"error": "Set a first frame before using Image-to-Video."},
                status=400,
            )

    if method == "frame_interpolation":
        if not clip.first_frame or not clip.first_frame.name:
            return JsonResponse(
                {"error": "Set a first frame before using Frame Interpolation."},
                status=400,
            )
        if not clip.last_frame or not clip.last_frame.name:
            return JsonResponse(
                {"error": "Set a last frame before using Frame Interpolation."},
                status=400,
            )

    task_id = run_in_background(
        "video_generation",
        generator_func,
        clip,
        related_object_id=clip.pk,
        related_object_type="clip",
    )

    return JsonResponse({"task_id": task_id}, status=202)


VALID_GENERATION_METHODS = {
    "text_to_video": generate_text_to_video,
    "image_to_video": generate_image_to_video,
    "frame_interpolation": generate_frame_interpolation,
}


def _get_generator_for_method(method):
    """Return the generator function for a given method name.

    Args:
        method: The generation method string.

    Returns:
        callable or None: The generator function, or None if invalid.
    """
    return VALID_GENERATION_METHODS.get(method)


# ── Reference Images ─────────────────────────────────────────────────────────

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_SLOTS = 3


@csrf_exempt
@require_POST
def api_generate_reference(request, project_id):
    """Generate a reference image via AI and save it to a slot.

    POST /api/projects/<id>/references/generate/
    Body JSON: {"slot_number": 1, "prompt": "...", "label": "..."}
    """
    project = get_object_or_404(Project, pk=project_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    slot_number = body.get("slot_number")
    prompt = body.get("prompt", "").strip()
    label = body.get("label", "").strip()

    validation_error = _validate_reference_input(slot_number, prompt, label)
    if validation_error:
        return validation_error

    task_id = run_in_background(
        "reference_image_generation",
        _generate_and_save_reference,
        project,
        slot_number,
        prompt,
        label,
        related_object_id=project.pk,
        related_object_type="project",
    )

    return JsonResponse({"task_id": task_id}, status=202)


def _validate_reference_input(slot_number, prompt, label):
    """Return a JsonResponse on validation failure, or None if valid."""
    if not isinstance(slot_number, int) or slot_number not in (1, 2, 3):
        return JsonResponse(
            {"error": "slot_number must be 1, 2, or 3."},
            status=400,
        )
    if not prompt:
        return JsonResponse({"error": "prompt is required."}, status=400)
    if not label:
        return JsonResponse({"error": "label is required."}, status=400)
    if len(label) > 100:
        return JsonResponse(
            {"error": "label must be 100 characters or fewer."},
            status=400,
        )
    return None


def _generate_and_save_reference(project, slot_number, prompt, label):
    """Background task: generate image, create/update ReferenceImage record.

    Args:
        project: Project instance.
        slot_number: Slot 1-3.
        prompt: AI prompt for image generation.
        label: Human label for the reference.

    Returns:
        dict: Result with image_url, label, and slot_number.
    """
    relative_path = generate_reference_image(prompt, project.pk, slot_number)

    ref, _ = ReferenceImage.objects.update_or_create(
        project=project,
        slot_number=slot_number,
        defaults={
            "image_file": relative_path,
            "label": label,
        },
    )

    return {
        "id": ref.pk,
        "slot_number": ref.slot_number,
        "label": ref.label,
        "image_url": f"/{settings.MEDIA_URL}{relative_path}",
    }


@csrf_exempt
@require_POST
def api_upload_reference(request, project_id):
    """Upload a reference image file to a slot.

    POST /api/projects/<id>/references/upload/
    Multipart form: slot_number, label, image (file).
    """
    project = get_object_or_404(Project, pk=project_id)

    slot_number = request.POST.get("slot_number")
    label = request.POST.get("label", "").strip()
    image = request.FILES.get("image")

    try:
        slot_number = int(slot_number) if slot_number else None
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "slot_number must be an integer."},
            status=400,
        )

    if not isinstance(slot_number, int) or slot_number not in (1, 2, 3):
        return JsonResponse(
            {"error": "slot_number must be 1, 2, or 3."},
            status=400,
        )

    if not label:
        return JsonResponse({"error": "label is required."}, status=400)

    if len(label) > 100:
        return JsonResponse(
            {"error": "label must be 100 characters or fewer."},
            status=400,
        )

    if not image:
        return JsonResponse({"error": "image file is required."}, status=400)

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse(
            {"error": "Image must be JPEG, PNG, or WebP."},
            status=400,
        )

    if image.size > MAX_IMAGE_SIZE_BYTES:
        return JsonResponse(
            {"error": "Image must be 10 MB or smaller."},
            status=400,
        )

    ref, _ = ReferenceImage.objects.update_or_create(
        project=project,
        slot_number=slot_number,
        defaults={"label": label},
    )
    ref.image_file.save(image.name, image, save=True)

    return JsonResponse(
        {
            "id": ref.pk,
            "slot_number": ref.slot_number,
            "label": ref.label,
            "image_url": ref.image_file.url,
        },
        status=201,
    )


@csrf_exempt
@require_POST
def api_delete_reference(request, project_id, slot_number):
    """Delete a reference image slot and remove file from disk.

    DELETE /api/projects/<id>/references/<slot>/
    """
    project = get_object_or_404(Project, pk=project_id)

    try:
        ref = ReferenceImage.objects.get(project=project, slot_number=slot_number)
    except ReferenceImage.DoesNotExist:
        return JsonResponse({"error": "Reference slot is empty."}, status=404)

    if ref.image_file and ref.image_file.name:
        try:
            ref.image_file.delete(save=False)
        except Exception:
            logger.warning("Failed to delete ref image file: %s", ref.image_file.name)

    ref_pk = ref.pk
    ref.delete()

    _remove_deleted_ref_from_clips(project, ref_pk)

    return JsonResponse({"status": "deleted", "slot_number": slot_number})


def _remove_deleted_ref_from_clips(project, deleted_ref_pk):
    """Remove a deleted reference PK from all clips' selected_references."""
    for clip in project.clips.all():
        if deleted_ref_pk in clip.selected_references:
            clip.selected_references = [
                pk for pk in clip.selected_references if pk != deleted_ref_pk
            ]
            clip.save(update_fields=["selected_references"])


@csrf_exempt
@require_POST
def api_update_clip_references(request, clip_id):
    """Update which reference images are selected for a clip.

    POST /api/clips/<id>/update-references/
    Body JSON: {"reference_ids": [1, 3]}
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    reference_ids = body.get("reference_ids")
    if not isinstance(reference_ids, list):
        return JsonResponse(
            {"error": "reference_ids must be a list."},
            status=400,
        )

    valid_ids = set(clip.project.reference_images.values_list("pk", flat=True))
    sanitized = [rid for rid in reference_ids if rid in valid_ids]

    clip.selected_references = sanitized
    clip.save(update_fields=["selected_references"])

    return JsonResponse({"status": "updated", "reference_ids": sanitized})


# ── First Frame Management ───────────────────────────────────────────────────

FIRST_FRAME_SOURCES = {"generate", "upload", "previous_clip"}


@csrf_exempt
@require_POST
def api_set_first_frame(request, clip_id):
    """Set the first frame for a clip.

    POST /api/clips/<id>/set-first-frame/

    Accepts either:
    - JSON {"source": "generate"} — generates a frame from the script
    - JSON {"source": "previous_clip"} — copies previous clip's last frame
    - Multipart form with "source": "upload" and "image" file
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    content_type = request.content_type or ""

    if "multipart" in content_type:
        return _handle_first_frame_upload(request, clip)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    source = body.get("source", "").strip()
    if source not in FIRST_FRAME_SOURCES:
        valid_sources = ", ".join(sorted(FIRST_FRAME_SOURCES))
        return JsonResponse(
            {"error": f"source must be one of: {valid_sources}."},
            status=400,
        )

    if source == "generate":
        return _handle_first_frame_generate(clip)

    if source == "previous_clip":
        return _handle_first_frame_from_previous(clip)

    return JsonResponse({"error": "Invalid source."}, status=400)


def _handle_first_frame_generate(clip):
    """Generate a first-frame image via AI in the background."""
    if not clip.script_text.strip():
        return JsonResponse(
            {"error": "Clip has no script text for frame generation."},
            status=400,
        )

    task_id = run_in_background(
        "first_frame_generation",
        _generate_and_save_first_frame,
        clip,
        related_object_id=clip.pk,
        related_object_type="clip",
    )

    return JsonResponse({"task_id": task_id}, status=202)


def _generate_and_save_first_frame(clip):
    """Background task: generate first frame image and save to clip.

    Args:
        clip: A Clip model instance.

    Returns:
        dict: Result with image_url and clip_id.
    """
    relative_path = generate_first_frame_image(clip)
    return {
        "clip_id": clip.pk,
        "image_url": f"/{settings.MEDIA_URL}{relative_path}",
    }


def _handle_first_frame_from_previous(clip):
    """Copy the previous clip's last frame as this clip's first frame."""
    if clip.sequence_number <= 1:
        return JsonResponse(
            {"error": "No previous clip exists for clip 1."},
            status=400,
        )

    previous_clip = Clip.objects.filter(
        project=clip.project,
        sequence_number=clip.sequence_number - 1,
    ).first()

    if not previous_clip:
        return JsonResponse(
            {"error": "Previous clip not found."},
            status=404,
        )

    if not previous_clip.last_frame or not previous_clip.last_frame.name:
        return JsonResponse(
            {"error": "Previous clip has no last frame set."},
            status=400,
        )

    from pathlib import Path

    from django.core.files.base import ContentFile

    source_path = Path(settings.MEDIA_ROOT) / previous_clip.last_frame.name
    if not source_path.exists():
        return JsonResponse(
            {"error": "Previous clip's last frame file not found."},
            status=404,
        )

    content = source_path.read_bytes()
    filename = f"first_{clip.project.pk}_{clip.sequence_number}" f"_from_prev.png"
    clip.first_frame.save(filename, ContentFile(content), save=True)

    return JsonResponse(
        {
            "status": "set",
            "clip_id": clip.pk,
            "image_url": clip.first_frame.url,
        }
    )


def _handle_first_frame_upload(request, clip):
    """Handle multipart upload of a first-frame image."""
    image = request.FILES.get("image")
    if not image:
        return JsonResponse(
            {"error": "image file is required."},
            status=400,
        )

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse(
            {"error": "Image must be JPEG, PNG, or WebP."},
            status=400,
        )

    if image.size > MAX_IMAGE_SIZE_BYTES:
        return JsonResponse(
            {"error": "Image must be 10 MB or smaller."},
            status=400,
        )

    clip.first_frame.save(image.name, image, save=True)

    return JsonResponse(
        {
            "status": "set",
            "clip_id": clip.pk,
            "image_url": clip.first_frame.url,
        }
    )


# ── Last Frame Management ────────────────────────────────────────────────────

LAST_FRAME_SOURCES = {"generate", "upload", "next_clip"}


@csrf_exempt
@require_POST
def api_set_last_frame(request, clip_id):
    """Set the last frame for a clip.

    POST /api/clips/<id>/set-last-frame/

    Accepts either:
    - JSON {"source": "generate"} — generates a frame from the script
    - JSON {"source": "next_clip"} — copies next clip's first frame
    - Multipart form with "source": "upload" and "image" file
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    content_type = request.content_type or ""

    if "multipart" in content_type:
        return _handle_last_frame_upload(request, clip)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    source = body.get("source", "").strip()
    if source not in LAST_FRAME_SOURCES:
        valid_sources = ", ".join(sorted(LAST_FRAME_SOURCES))
        return JsonResponse(
            {"error": f"source must be one of: {valid_sources}."},
            status=400,
        )

    if source == "generate":
        return _handle_last_frame_generate(clip)

    if source == "next_clip":
        return _handle_last_frame_from_next(clip)

    return JsonResponse({"error": "Invalid source."}, status=400)


def _handle_last_frame_generate(clip):
    """Generate a last-frame image via AI in the background."""
    if not clip.script_text.strip():
        return JsonResponse(
            {"error": "Clip has no script text for frame generation."},
            status=400,
        )

    task_id = run_in_background(
        "last_frame_generation",
        _generate_and_save_last_frame,
        clip,
        related_object_id=clip.pk,
        related_object_type="clip",
    )

    return JsonResponse({"task_id": task_id}, status=202)


def _generate_and_save_last_frame(clip):
    """Background task: generate last frame image and save to clip.

    Args:
        clip: A Clip model instance.

    Returns:
        dict: Result with image_url and clip_id.
    """
    relative_path = generate_last_frame_image(clip)
    return {
        "clip_id": clip.pk,
        "image_url": f"/{settings.MEDIA_URL}{relative_path}",
    }


def _handle_last_frame_from_next(clip):
    """Copy the next clip's first frame as this clip's last frame."""
    from pathlib import Path

    from django.core.files.base import ContentFile

    next_clip = Clip.objects.filter(
        project=clip.project,
        sequence_number=clip.sequence_number + 1,
    ).first()

    if not next_clip:
        return JsonResponse(
            {"error": "No next clip exists."},
            status=400,
        )

    if not next_clip.first_frame or not next_clip.first_frame.name:
        return JsonResponse(
            {"error": "Next clip has no first frame set."},
            status=400,
        )

    source_path = Path(settings.MEDIA_ROOT) / next_clip.first_frame.name
    if not source_path.exists():
        return JsonResponse(
            {"error": "Next clip's first frame file not found."},
            status=404,
        )

    content = source_path.read_bytes()
    filename = f"last_{clip.project.pk}_{clip.sequence_number}_from_next.png"
    clip.last_frame.save(filename, ContentFile(content), save=True)

    return JsonResponse(
        {
            "status": "set",
            "clip_id": clip.pk,
            "image_url": clip.last_frame.url,
        }
    )


def _handle_last_frame_upload(request, clip):
    """Handle multipart upload of a last-frame image."""
    image = request.FILES.get("image")
    if not image:
        return JsonResponse(
            {"error": "image file is required."},
            status=400,
        )

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse(
            {"error": "Image must be JPEG, PNG, or WebP."},
            status=400,
        )

    if image.size > MAX_IMAGE_SIZE_BYTES:
        return JsonResponse(
            {"error": "Image must be 10 MB or smaller."},
            status=400,
        )

    clip.last_frame.save(image.name, image, save=True)

    return JsonResponse(
        {
            "status": "set",
            "clip_id": clip.pk,
            "image_url": clip.last_frame.url,
        }
    )


# ── Clip Management ──────────────────────────────────────────────────────────

MAX_CLIPS_PER_PROJECT = 10


@csrf_exempt
@require_POST
def api_reorder_clips(request, project_id):
    """Reorder clips within a project.

    POST /api/projects/<id>/clips/reorder/
    Body JSON: {"clip_ids": [3, 1, 5, 2, 4]}
    """
    project = get_object_or_404(Project, pk=project_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    clip_ids = body.get("clip_ids")
    if not isinstance(clip_ids, list):
        return JsonResponse(
            {"error": "clip_ids must be a list."},
            status=400,
        )

    project_clip_ids = set(project.clips.values_list("pk", flat=True))

    if set(clip_ids) != project_clip_ids:
        return JsonResponse(
            {"error": "clip_ids must contain exactly all clip IDs for the project."},
            status=400,
        )

    if len(clip_ids) != len(set(clip_ids)):
        return JsonResponse(
            {"error": "clip_ids must not contain duplicates."},
            status=400,
        )

    for new_seq, clip_id in enumerate(clip_ids, start=1):
        Clip.objects.filter(pk=clip_id).update(sequence_number=-new_seq)

    Clip.objects.filter(project=project, sequence_number__lt=0).update(
        sequence_number=-F("sequence_number")
    )

    return JsonResponse({"status": "reordered"})


@csrf_exempt
@require_POST
def api_add_clip(request, project_id):
    """Add a new empty clip at the end of the project's sequence.

    POST /api/projects/<id>/clips/add/
    Returns JSON with the new clip data.
    """
    project = get_object_or_404(Project, pk=project_id)

    current_count = project.clips.count()
    if current_count >= MAX_CLIPS_PER_PROJECT:
        return JsonResponse(
            {"error": "Maximum of 10 clips per project."},
            status=400,
        )

    last_clip = project.clips.order_by("-sequence_number").first()
    next_seq = (last_clip.sequence_number + 1) if last_clip else 1

    clip = Clip.objects.create(
        project=project,
        sequence_number=next_seq,
        script_text="",
    )

    return JsonResponse(
        {
            "status": "added",
            "clip": {
                "id": clip.pk,
                "sequence_number": clip.sequence_number,
                "script_text": clip.script_text,
                "generation_status": clip.generation_status,
                "generation_method": clip.generation_method,
            },
        },
        status=201,
    )


@csrf_exempt
@require_POST
def api_delete_clip(request, clip_id):
    """Delete a clip and resequence remaining clips.

    POST /api/clips/<id>/delete/
    Deletes associated video/image files from disk.
    """
    clip = get_object_or_404(Clip, pk=clip_id)
    project = clip.project

    if project.clips.count() <= 1:
        return JsonResponse(
            {"error": "Cannot delete the last clip. Minimum is 1 clip."},
            status=400,
        )

    _delete_clip_media(clip)
    deleted_seq = clip.sequence_number
    clip.delete()

    remaining = project.clips.order_by("sequence_number")
    for new_seq, remaining_clip in enumerate(remaining, start=1):
        if remaining_clip.sequence_number != new_seq:
            remaining_clip.sequence_number = new_seq
            remaining_clip.save(update_fields=["sequence_number"])

    return JsonResponse(
        {
            "status": "deleted",
            "deleted_sequence": deleted_seq,
        }
    )


def _delete_clip_media(clip):
    """Remove media files from disk for a single clip."""
    if clip.video_file and clip.video_file.name:
        try:
            clip.video_file.delete(save=False)
        except Exception:
            logger.warning("Failed to delete video: %s", clip.video_file.name)
    if clip.first_frame and clip.first_frame.name:
        try:
            clip.first_frame.delete(save=False)
        except Exception:
            logger.warning("Failed to delete frame: %s", clip.first_frame.name)
    if clip.last_frame and clip.last_frame.name:
        try:
            clip.last_frame.delete(save=False)
        except Exception:
            logger.warning("Failed to delete frame: %s", clip.last_frame.name)


# ── Script Regeneration ──────────────────────────────────────────────────────


@csrf_exempt
@require_POST
def api_regenerate_clip_script(request, clip_id):
    """Regenerate a single clip's script using AI with neighbor context.

    POST /api/clips/<id>/regenerate-script/

    Calls the Gemini API to rewrite this clip's script while
    maintaining coherence with neighboring clips. Returns the new
    script text as JSON.

    Returns JSON {"status": "regenerated", "clip_id": <int>,
    "script_text": <str>} with HTTP 200 on success.
    """
    clip = get_object_or_404(Clip, pk=clip_id)

    try:
        new_script = regenerate_single_script(clip)
    except Exception:
        logger.warning(
            "Script regeneration failed for clip %d",
            clip.pk,
            exc_info=True,
        )
        return JsonResponse(
            {"error": "Script regeneration failed. Please try again."},
            status=500,
        )

    clip.script_text = new_script
    clip.save(update_fields=["script_text"])

    return JsonResponse(
        {
            "status": "regenerated",
            "clip_id": clip.pk,
            "script_text": new_script,
        }
    )


@csrf_exempt
@require_POST
def api_regenerate_all_scripts(request, project_id):
    """Regenerate all clip scripts for a project from scratch.

    POST /api/projects/<id>/regenerate-all-scripts/

    Calls the Gemini API to rewrite every clip's script based on
    the current project metadata. Returns the new scripts as JSON.

    Returns JSON {"status": "regenerated", "scripts": [
        {"clip_id": <int>, "sequence_number": <int>,
         "script_text": <str>}, ...
    ]} with HTTP 200 on success.
    """
    project = get_object_or_404(Project, pk=project_id)
    clips = list(project.clips.order_by("sequence_number"))

    if not clips:
        return JsonResponse(
            {"error": "Project has no clips to regenerate."},
            status=400,
        )

    try:
        new_scripts = regenerate_all_scripts(project)
    except Exception:
        logger.warning(
            "Full script regeneration failed for project '%s'",
            project.title,
            exc_info=True,
        )
        return JsonResponse(
            {"error": "Script regeneration failed. Please try again."},
            status=500,
        )

    scripts_response = []
    for clip, script in zip(clips, new_scripts):
        clip.script_text = script
        clip.save(update_fields=["script_text"])
        scripts_response.append(
            {
                "clip_id": clip.pk,
                "sequence_number": clip.sequence_number,
                "script_text": script,
            }
        )

    return JsonResponse(
        {
            "status": "regenerated",
            "scripts": scripts_response,
        }
    )
