"""Admin configuration for the core app."""

from django.contrib import admin

from core.models import Clip, Hook, Project, ReferenceImage, Task, UserSettings


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin view for Project model."""

    list_display = ("title", "aspect_ratio", "clip_duration", "num_clips", "updated_at")
    search_fields = ("title",)


@admin.register(Clip)
class ClipAdmin(admin.ModelAdmin):
    """Admin view for Clip model."""

    list_display = (
        "project",
        "sequence_number",
        "generation_status",
        "generation_method",
    )
    list_filter = ("generation_status", "generation_method")


@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    """Admin view for ReferenceImage model."""

    list_display = ("project", "slot_number", "label")


@admin.register(Hook)
class HookAdmin(admin.ModelAdmin):
    """Admin view for Hook model."""

    list_display = ("project", "is_enabled", "generation_status")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin view for UserSettings singleton."""

    list_display = ("default_aspect_ratio", "default_clip_duration", "video_quality")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin view for Task model."""

    list_display = ("task_type", "status", "progress", "created_at")
    list_filter = ("status", "task_type")
