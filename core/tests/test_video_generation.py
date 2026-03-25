"""Tests for the text-to-video generation service and API endpoint."""

from unittest.mock import MagicMock, patch

import pytest

from django.test import Client

from core.models import Clip, Project, Task, UserSettings
from core.services.ai_client import reset_client
from core.services.video_generator import (
    _build_video_config,
    _get_user_settings,
    _get_veo_model,
    generate_text_to_video,
)


@pytest.fixture(autouse=True)
def _reset_ai_client():
    """Reset the AI client singleton before each test."""
    reset_client()
    yield
    reset_client()


@pytest.fixture()
def project(db):
    """Create a test project."""
    return Project.objects.create(
        title="Video Test Reel",
        description="A reel for testing video generation",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )


@pytest.fixture()
def clip(project):
    """Create a test clip with script text."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="A cinematic shot of a city at night with neon lights",
    )


@pytest.fixture()
def clip_no_script(project):
    """Create a test clip without script text."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="",
    )


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


class TestGetVeoModel:
    """Tests for the _get_veo_model helper."""

    def test_returns_quality_model_by_default(self):
        assert _get_veo_model("quality") == "veo-3.1-generate-preview"

    def test_returns_fast_model(self):
        assert _get_veo_model("fast") == "veo-3.1-fast-generate-preview"


class TestGetUserSettings:
    """Tests for the _get_user_settings helper."""

    @pytest.mark.django_db
    def test_returns_defaults_when_no_settings_exist(self):
        result = _get_user_settings()
        assert result["video_quality"] == "720p"
        assert result["generation_speed"] == "quality"

    @pytest.mark.django_db
    def test_returns_saved_settings(self):
        settings = UserSettings.load()
        settings.video_quality = "1080p"
        settings.generation_speed = "fast"
        settings.save()

        result = _get_user_settings()
        assert result["video_quality"] == "1080p"
        assert result["generation_speed"] == "fast"


class TestBuildVideoConfig:
    """Tests for the _build_video_config helper."""

    @pytest.mark.django_db
    def test_builds_config_with_project_settings(self, clip):
        user_settings = {"video_quality": "720p", "generation_speed": "quality"}
        config = _build_video_config(clip, user_settings)

        assert config.aspect_ratio == "9:16"
        assert config.resolution == "720p"
        assert config.duration_seconds == 8
        assert config.number_of_videos == 1

    @pytest.mark.django_db
    def test_forces_8s_duration_for_high_res(self, project):
        project.clip_duration = 4
        project.save()
        clip = Clip.objects.create(
            project=project,
            sequence_number=10,
            script_text="test",
        )
        user_settings = {"video_quality": "1080p", "generation_speed": "quality"}
        config = _build_video_config(clip, user_settings)

        assert config.duration_seconds == 8

    @pytest.mark.django_db
    def test_keeps_duration_for_720p(self, project):
        project.clip_duration = 4
        project.save()
        clip = Clip.objects.create(
            project=project,
            sequence_number=10,
            script_text="test",
        )
        user_settings = {"video_quality": "720p", "generation_speed": "quality"}
        config = _build_video_config(clip, user_settings)

        assert config.duration_seconds == 4


@pytest.mark.django_db(transaction=True)
class TestGenerateTextToVideo:
    """Tests for the generate_text_to_video service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_sets_status_to_generating_then_completed(self, mock_get_client, clip):
        """Successful generation should transition idle -> generating -> completed."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/test-op-123"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation

        result = generate_text_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "completed"
        assert clip.generation_reference_id == "operations/test-op-123"
        assert result["clip_id"] == clip.pk
        assert "video_url" in result

    @patch("core.services.video_generator.get_ai_client")
    def test_handles_api_failure(self, mock_get_client, clip):
        """API failure should set status to failed and raise RuntimeError."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_videos.side_effect = Exception("API down")

        with pytest.raises(RuntimeError, match="Video generation failed"):
            generate_text_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"

    @pytest.mark.django_db
    def test_rejects_empty_script(self, clip_no_script):
        """A clip with no script should raise ValueError."""
        with pytest.raises(ValueError, match="no script text"):
            generate_text_to_video(clip_no_script)

        clip_no_script.refresh_from_db()
        assert clip_no_script.generation_status == "failed"

    @patch("core.services.video_generator.get_ai_client")
    def test_polls_until_done(self, mock_get_client, clip):
        """Should poll the operation when not immediately done."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        pending_op = MagicMock()
        pending_op.done = False

        done_op = MagicMock()
        done_op.done = True
        done_op.name = "operations/poll-test"
        done_op.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = pending_op
        mock_client.operations.get.return_value = done_op

        with patch("core.services.video_generator.time.sleep"):
            generate_text_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "completed"
        mock_client.operations.get.assert_called_once()

    @patch("core.services.video_generator.get_ai_client")
    def test_uses_correct_model_name(self, mock_get_client, clip):
        """Should use the Veo model based on user settings."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "op-model-test"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation

        generate_text_to_video(clip)

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs["model"] == "veo-3.1-generate-preview"


@pytest.mark.django_db
class TestGenerateVideoEndpoint:
    """Tests for the POST /api/clips/<id>/generate-video/ endpoint."""

    def test_returns_202_with_task_id(self, api_client, clip):
        """Successful POST should return 202 with a task_id."""
        with patch("core.views.generate_text_to_video"):
            response = api_client.post(
                f"/api/clips/{clip.pk}/generate-video/",
                content_type="application/json",
            )

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data

    def test_returns_400_for_empty_script(self, api_client, clip_no_script):
        """POST with an empty-script clip should return 400."""
        response = api_client.post(
            f"/api/clips/{clip_no_script.pk}/generate-video/",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "script" in response.json()["error"].lower()

    def test_returns_404_for_nonexistent_clip(self, api_client):
        """POST for a nonexistent clip should return 404."""
        response = api_client.post(
            "/api/clips/99999/generate-video/",
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_returns_409_if_already_generating(self, api_client, clip):
        """POST while clip is already generating should return 409."""
        clip.generation_status = "generating"
        clip.save()

        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            content_type="application/json",
        )

        assert response.status_code == 409
        assert "already in progress" in response.json()["error"].lower()

    def test_creates_background_task(self, api_client, clip):
        """POST should create a Task record in the database."""
        with patch("core.views.generate_text_to_video"):
            response = api_client.post(
                f"/api/clips/{clip.pk}/generate-video/",
                content_type="application/json",
            )

        task_id = response.json()["task_id"]
        task = Task.objects.get(pk=task_id)
        assert task.task_type == "video_generation"
        assert task.related_object_id == clip.pk
        assert task.related_object_type == "clip"
