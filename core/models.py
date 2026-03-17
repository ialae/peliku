"""Models for the core app."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ASPECT_RATIO_CHOICES = [
    ("9:16", "Portrait (9:16)"),
    ("16:9", "Landscape (16:9)"),
]

CLIP_DURATION_CHOICES = [
    (4, "4 seconds"),
    (6, "6 seconds"),
    (8, "8 seconds"),
]

GENERATION_STATUS_CHOICES = [
    ("idle", "Idle"),
    ("generating", "Generating"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]

GENERATION_METHOD_CHOICES = [
    ("text_to_video", "Text to Video"),
    ("image_to_video", "Image to Video"),
    ("frame_interpolation", "Frame Interpolation"),
    ("extend_previous", "Extend from Previous Clip"),
]

TASK_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]

VIDEO_QUALITY_CHOICES = [
    ("720p", "720p"),
    ("1080p", "1080p"),
    ("4k", "4K"),
]

GENERATION_SPEED_CHOICES = [
    ("quality", "Quality"),
    ("fast", "Fast"),
]


class Project(models.Model):
    """A reel project containing clips, references, and settings."""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    visual_style = models.TextField(max_length=500, blank=True, default="")
    aspect_ratio = models.CharField(
        max_length=5,
        choices=ASPECT_RATIO_CHOICES,
        default="9:16",
    )
    clip_duration = models.IntegerField(
        choices=CLIP_DURATION_CHOICES,
        default=8,
    )
    num_clips = models.IntegerField(
        default=7,
        validators=[MinValueValidator(5), MaxValueValidator(10)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class Clip(models.Model):
    """A single video clip within a project."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="clips",
    )
    sequence_number = models.IntegerField()
    script_text = models.TextField(blank=True, default="")
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        default="",
    )
    generation_status = models.CharField(
        max_length=20,
        choices=GENERATION_STATUS_CHOICES,
        default="idle",
    )
    generation_method = models.CharField(
        max_length=30,
        choices=GENERATION_METHOD_CHOICES,
        default="text_to_video",
    )
    first_frame = models.ImageField(
        upload_to="images/frames/",
        blank=True,
        default="",
    )
    last_frame = models.ImageField(
        upload_to="images/frames/",
        blank=True,
        default="",
    )
    extension_count = models.IntegerField(default=0)
    generation_reference_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ["sequence_number"]
        unique_together = [("project", "sequence_number")]

    def __str__(self):
        return f"{self.project.title} — Clip {self.sequence_number}"


class ReferenceImage(models.Model):
    """A reference image slot used for visual consistency."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="reference_images",
    )
    slot_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )
    image_file = models.ImageField(upload_to="images/references/")
    label = models.CharField(max_length=100)

    class Meta:
        unique_together = [("project", "slot_number")]

    def __str__(self):
        return f"{self.project.title} — Ref {self.slot_number}: {self.label}"


class Hook(models.Model):
    """An optional hook clip prepended to a project's reel."""

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="hook",
    )
    script_text = models.TextField(blank=True, default="")
    video_file = models.FileField(
        upload_to="videos/hooks/",
        blank=True,
        default="",
    )
    is_enabled = models.BooleanField(default=False)
    generation_status = models.CharField(
        max_length=20,
        choices=GENERATION_STATUS_CHOICES,
        default="idle",
    )

    def __str__(self):
        return f"{self.project.title} — Hook"


class UserSettings(models.Model):
    """Singleton model storing global user preferences."""

    default_aspect_ratio = models.CharField(
        max_length=5,
        choices=ASPECT_RATIO_CHOICES,
        default="9:16",
    )
    default_clip_duration = models.IntegerField(
        choices=CLIP_DURATION_CHOICES,
        default=8,
    )
    default_num_clips = models.IntegerField(
        default=7,
        validators=[MinValueValidator(5), MaxValueValidator(10)],
    )
    default_visual_style = models.TextField(
        max_length=500,
        blank=True,
        default="",
    )
    video_quality = models.CharField(
        max_length=5,
        choices=VIDEO_QUALITY_CHOICES,
        default="720p",
    )
    generation_speed = models.CharField(
        max_length=10,
        choices=GENERATION_SPEED_CHOICES,
        default="quality",
    )

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return "User Settings"

    def save(self, *args, **kwargs):
        """Enforce singleton: always use pk=1."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the singleton instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Task(models.Model):
    """Tracks asynchronous background task status."""

    task_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default="pending",
    )
    progress = models.IntegerField(default=0)
    result_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, default="")
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return f"Task {self.pk}: {self.task_type} ({self.status})"
