"""URL configuration for the core app."""

from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/new/", views.project_form, name="project_form"),
    path(
        "projects/<int:project_id>/",
        views.workspace,
        name="workspace",
    ),
    path(
        "api/projects/<int:project_id>/delete/",
        views.api_delete_project,
        name="api_delete_project",
    ),
    path(
        "api/projects/<int:project_id>/rename/",
        views.api_rename_project,
        name="api_rename_project",
    ),
    path(
        "api/projects/<int:project_id>/duplicate/",
        views.api_duplicate_project,
        name="api_duplicate_project",
    ),
    path(
        "api/clips/<int:clip_id>/update-script/",
        views.api_update_clip_script,
        name="api_update_clip_script",
    ),
    path(
        "api/clips/<int:clip_id>/update-method/",
        views.api_update_generation_method,
        name="api_update_generation_method",
    ),
    path(
        "api/tasks/<int:task_id>/status/",
        views.api_task_status,
        name="api_task_status",
    ),
    path(
        "api/clips/<int:clip_id>/generate-video/",
        views.api_generate_video,
        name="api_generate_video",
    ),
    path(
        "api/projects/<int:project_id>/references/generate/",
        views.api_generate_reference,
        name="api_generate_reference",
    ),
    path(
        "api/projects/<int:project_id>/references/upload/",
        views.api_upload_reference,
        name="api_upload_reference",
    ),
    path(
        "api/projects/<int:project_id>/references/<int:slot_number>/delete/",
        views.api_delete_reference,
        name="api_delete_reference",
    ),
    path(
        "api/clips/<int:clip_id>/update-references/",
        views.api_update_clip_references,
        name="api_update_clip_references",
    ),
    path(
        "api/clips/<int:clip_id>/set-first-frame/",
        views.api_set_first_frame,
        name="api_set_first_frame",
    ),
    path(
        "api/clips/<int:clip_id>/set-last-frame/",
        views.api_set_last_frame,
        name="api_set_last_frame",
    ),
    path(
        "api/projects/<int:project_id>/clips/reorder/",
        views.api_reorder_clips,
        name="api_reorder_clips",
    ),
    path(
        "api/projects/<int:project_id>/clips/add/",
        views.api_add_clip,
        name="api_add_clip",
    ),
    path(
        "api/clips/<int:clip_id>/delete/",
        views.api_delete_clip,
        name="api_delete_clip",
    ),
    path(
        "api/clips/<int:clip_id>/regenerate-script/",
        views.api_regenerate_clip_script,
        name="api_regenerate_clip_script",
    ),
    path(
        "api/projects/<int:project_id>/regenerate-all-scripts/",
        views.api_regenerate_all_scripts,
        name="api_regenerate_all_scripts",
    ),
]
