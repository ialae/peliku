"""Views for the core app."""

import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.forms import ProjectForm
from core.models import Clip, Project, ReferenceImage, Task, UserSettings
from core.services.script_generator import generate_all_scripts

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

    context = {
        "project": project,
        "clips": clips,
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
