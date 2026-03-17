"""Tests for core models: creation, validation, relationships, and behavior."""

import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from core.models import Clip, Hook, Project, ReferenceImage, Task, UserSettings


@pytest.mark.django_db
class TestProject:
    """Tests for the Project model."""

    def test_create_project_with_defaults(self):
        project = Project.objects.create(
            title="Test Reel",
            description="A test reel about nature.",
        )

        assert project.pk is not None
        assert project.title == "Test Reel"
        assert project.aspect_ratio == "9:16"
        assert project.clip_duration == 8
        assert project.num_clips == 7
        assert project.visual_style == ""
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_create_project_with_all_fields(self):
        project = Project.objects.create(
            title="Custom Reel",
            description="A reel with custom settings.",
            visual_style="Cinematic, moody tones",
            aspect_ratio="16:9",
            clip_duration=6,
            num_clips=10,
        )

        assert project.aspect_ratio == "16:9"
        assert project.clip_duration == 6
        assert project.num_clips == 10
        assert project.visual_style == "Cinematic, moody tones"

    def test_project_str_returns_title(self):
        project = Project(title="My Reel")

        assert str(project) == "My Reel"

    def test_project_ordering_by_updated_at_desc(self):
        first = Project.objects.create(title="First", description="d")
        second = Project.objects.create(title="Second", description="d")
        # Touch first to make it most recently updated
        first.title = "First Updated"
        first.save()

        projects = list(Project.objects.all())

        assert projects[0].pk == first.pk
        assert projects[1].pk == second.pk

    def test_num_clips_validator_rejects_below_minimum(self):
        project = Project(
            title="Bad",
            description="d",
            num_clips=3,
        )

        with pytest.raises(ValidationError):
            project.full_clean()

    def test_num_clips_validator_rejects_above_maximum(self):
        project = Project(
            title="Bad",
            description="d",
            num_clips=15,
        )

        with pytest.raises(ValidationError):
            project.full_clean()


@pytest.mark.django_db
class TestClip:
    """Tests for the Clip model."""

    def test_create_clip_with_defaults(self):
        project = Project.objects.create(title="P", description="d")
        clip = Clip.objects.create(project=project, sequence_number=1)

        assert clip.pk is not None
        assert clip.script_text == ""
        assert clip.generation_status == "idle"
        assert clip.generation_method == "text_to_video"
        assert clip.extension_count == 0
        assert clip.generation_reference_id == ""

    def test_clip_str_representation(self):
        project = Project.objects.create(title="My Reel", description="d")
        clip = Clip.objects.create(project=project, sequence_number=3)

        assert str(clip) == "My Reel — Clip 3"

    def test_clips_ordered_by_sequence_number(self):
        project = Project.objects.create(title="P", description="d")
        Clip.objects.create(project=project, sequence_number=3)
        Clip.objects.create(project=project, sequence_number=1)
        Clip.objects.create(project=project, sequence_number=2)

        clips = list(project.clips.all())

        assert [c.sequence_number for c in clips] == [1, 2, 3]

    def test_clip_unique_together_project_sequence(self):
        project = Project.objects.create(title="P", description="d")
        Clip.objects.create(project=project, sequence_number=1)

        with pytest.raises(IntegrityError):
            Clip.objects.create(project=project, sequence_number=1)

    def test_cascade_delete_removes_clips(self):
        project = Project.objects.create(title="P", description="d")
        Clip.objects.create(project=project, sequence_number=1)
        Clip.objects.create(project=project, sequence_number=2)

        project.delete()

        assert Clip.objects.count() == 0


@pytest.mark.django_db
class TestReferenceImage:
    """Tests for the ReferenceImage model."""

    def test_create_reference_image(self):
        project = Project.objects.create(title="P", description="d")
        ref = ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/test.png",
            label="Main character",
        )

        assert ref.pk is not None
        assert ref.slot_number == 1
        assert ref.label == "Main character"

    def test_reference_str_representation(self):
        project = Project.objects.create(title="My Reel", description="d")
        ref = ReferenceImage.objects.create(
            project=project,
            slot_number=2,
            image_file="images/references/test.png",
            label="Red car",
        )

        assert str(ref) == "My Reel — Ref 2: Red car"

    def test_unique_together_project_slot(self):
        project = Project.objects.create(title="P", description="d")
        ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/a.png",
            label="A",
        )

        with pytest.raises(IntegrityError):
            ReferenceImage.objects.create(
                project=project,
                slot_number=1,
                image_file="images/references/b.png",
                label="B",
            )

    def test_slot_number_validator_rejects_invalid(self):
        project = Project.objects.create(title="P", description="d")
        ref = ReferenceImage(
            project=project,
            slot_number=5,
            image_file="images/references/test.png",
            label="Bad",
        )

        with pytest.raises(ValidationError):
            ref.full_clean()

    def test_cascade_delete_removes_references(self):
        project = Project.objects.create(title="P", description="d")
        ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/test.png",
            label="A",
        )

        project.delete()

        assert ReferenceImage.objects.count() == 0


@pytest.mark.django_db
class TestHook:
    """Tests for the Hook model."""

    def test_create_hook_with_defaults(self):
        project = Project.objects.create(title="P", description="d")
        hook = Hook.objects.create(project=project)

        assert hook.pk is not None
        assert hook.script_text == ""
        assert hook.is_enabled is False
        assert hook.generation_status == "idle"

    def test_hook_str_representation(self):
        project = Project.objects.create(title="My Reel", description="d")
        hook = Hook.objects.create(project=project)

        assert str(hook) == "My Reel — Hook"

    def test_one_to_one_prevents_duplicate_hook(self):
        project = Project.objects.create(title="P", description="d")
        Hook.objects.create(project=project)

        with pytest.raises(IntegrityError):
            Hook.objects.create(project=project)

    def test_cascade_delete_removes_hook(self):
        project = Project.objects.create(title="P", description="d")
        Hook.objects.create(project=project)

        project.delete()

        assert Hook.objects.count() == 0


@pytest.mark.django_db
class TestUserSettings:
    """Tests for the UserSettings singleton model."""

    def test_load_creates_default_settings(self):
        settings = UserSettings.load()

        assert settings.pk == 1
        assert settings.default_aspect_ratio == "9:16"
        assert settings.default_clip_duration == 8
        assert settings.default_num_clips == 7
        assert settings.default_visual_style == ""
        assert settings.video_quality == "720p"
        assert settings.generation_speed == "quality"

    def test_load_returns_existing_settings(self):
        UserSettings.objects.create(
            pk=1,
            default_aspect_ratio="16:9",
            video_quality="1080p",
        )

        settings = UserSettings.load()

        assert settings.default_aspect_ratio == "16:9"
        assert settings.video_quality == "1080p"

    def test_singleton_enforced_on_save(self):
        settings_a = UserSettings(default_aspect_ratio="16:9")
        settings_a.save()

        settings_b = UserSettings(default_aspect_ratio="9:16")
        settings_b.save()

        assert UserSettings.objects.count() == 1
        reloaded = UserSettings.objects.get(pk=1)
        assert reloaded.default_aspect_ratio == "9:16"

    def test_settings_str_representation(self):
        settings = UserSettings()

        assert str(settings) == "User Settings"


@pytest.mark.django_db
class TestTask:
    """Tests for the Task model."""

    def test_create_task_with_defaults(self):
        task = Task.objects.create(task_type="video_generation")

        assert task.pk is not None
        assert task.status == "pending"
        assert task.progress == 0
        assert task.result_data is None
        assert task.error_message == ""
        assert task.related_object_id is None
        assert task.related_object_type == ""

    def test_task_str_representation(self):
        task = Task.objects.create(task_type="script_generation")

        assert str(task) == f"Task {task.pk}: script_generation (pending)"

    def test_task_with_result_data(self):
        task = Task.objects.create(
            task_type="video_generation",
            status="completed",
            progress=100,
            result_data={"video_url": "https://example.com/video.mp4"},
            related_object_id=42,
            related_object_type="Clip",
        )

        assert task.result_data["video_url"] == "https://example.com/video.mp4"
        assert task.related_object_id == 42
        assert task.related_object_type == "Clip"

    def test_tasks_ordered_by_created_at_desc(self):
        task_a = Task.objects.create(task_type="a")
        task_b = Task.objects.create(task_type="b")

        tasks = list(Task.objects.all())

        assert tasks[0].pk == task_b.pk
        assert tasks[1].pk == task_a.pk
