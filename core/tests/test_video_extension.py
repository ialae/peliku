"""Tests for the video extension service and API endpoint."""

import json
from unittest.mock import MagicMock, patch

import pytest

from django.test import Client

from core.models import Clip, Project
from core.services.ai_client import reset_client
from core.services.video_extender import MAX_EXTENSIONS, extend_clip_video


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
        title="Extension Test Reel",
        description="A reel for testing video extension",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )


@pytest.fixture()
def clip_with_video(project):
    """Create a clip with a completed video and generation reference."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="A cinematic city scene",
        video_file="videos/clip_1_1.mp4",
        generation_status="completed",
        generation_reference_id="operations/test-ref-123",
        extension_count=0,
    )


@pytest.fixture()
def clip_no_video(project):
    """Create a clip without a video file."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="Some text",
        generation_status="idle",
    )


@pytest.fixture()
def clip_no_reference(project):
    """Create a clip with video but no generation reference ID."""
    return Clip.objects.create(
        project=project,
        sequence_number=3,
        script_text="Some text",
        video_file="videos/clip_1_3.mp4",
        generation_status="completed",
        generation_reference_id="",
    )


@pytest.fixture()
def clip_max_extensions(project):
    """Create a clip that has reached the max extension limit."""
    return Clip.objects.create(
        project=project,
        sequence_number=4,
        script_text="Some text",
        video_file="videos/clip_1_4.mp4",
        generation_status="completed",
        generation_reference_id="operations/test-ref-456",
        extension_count=MAX_EXTENSIONS,
    )


@pytest.fixture()
def clip_generating(project):
    """Create a clip currently generating."""
    return Clip.objects.create(
        project=project,
        sequence_number=5,
        script_text="Some text",
        video_file="videos/clip_1_5.mp4",
        generation_status="generating",
        generation_reference_id="operations/test-ref-789",
    )


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


# ── Service Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestExtendClipVideoService:
    """Tests for the extend_clip_video service function."""

    @patch("core.services.video_extender.get_ai_client")
    def test_successful_extension(self, mock_get_client, clip_with_video, tmp_path):
        """Successful extension updates clip fields and returns result data."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/extended-ref-001"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.files.download = MagicMock()

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
            result = extend_clip_video(clip_with_video, "Continue the scene")

        clip_with_video.refresh_from_db()
        assert clip_with_video.generation_status == "completed"
        assert clip_with_video.extension_count == 1
        assert clip_with_video.generation_reference_id == "operations/extended-ref-001"
        assert "video_url" in result
        assert result["clip_id"] == clip_with_video.pk
        assert result["extension_count"] == 1

    def test_raises_when_no_video(self, clip_no_video):
        """Should raise ValueError when clip has no video file."""
        with pytest.raises(ValueError, match="no generated video"):
            extend_clip_video(clip_no_video, "Continue the scene")

    def test_raises_when_no_reference_id(self, clip_no_reference):
        """Should raise ValueError when clip has no generation reference."""
        with pytest.raises(ValueError, match="no generation reference ID"):
            extend_clip_video(clip_no_reference, "Continue the scene")

    def test_raises_when_max_extensions_reached(self, clip_max_extensions):
        """Should raise ValueError when extension limit is reached."""
        with pytest.raises(ValueError, match="Maximum extension limit"):
            extend_clip_video(clip_max_extensions, "Continue the scene")

    def test_raises_when_prompt_empty(self, clip_with_video):
        """Should raise ValueError when prompt is empty."""
        with pytest.raises(ValueError, match="Extension prompt is required"):
            extend_clip_video(clip_with_video, "")

    def test_raises_when_prompt_whitespace_only(self, clip_with_video):
        """Should raise ValueError when prompt is only whitespace."""
        with pytest.raises(ValueError, match="Extension prompt is required"):
            extend_clip_video(clip_with_video, "   ")

    @patch("core.services.video_extender.get_ai_client")
    def test_sets_status_to_failed_on_api_error(self, mock_get_client, clip_with_video):
        """Should set status to 'failed' when the API call raises."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_videos.side_effect = RuntimeError("API error")

        with pytest.raises(RuntimeError, match="Video extension failed"):
            extend_clip_video(clip_with_video, "Continue the scene")

        clip_with_video.refresh_from_db()
        assert clip_with_video.generation_status == "failed"

    @patch("core.services.video_extender.get_ai_client")
    def test_increments_extension_count(
        self, mock_get_client, clip_with_video, tmp_path
    ):
        """Each extension should increment extension_count by one."""
        clip_with_video.extension_count = 5
        clip_with_video.save(update_fields=["extension_count"])

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/ext-ref-002"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.files.download = MagicMock()

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
            result = extend_clip_video(clip_with_video, "Continue the scene")

        clip_with_video.refresh_from_db()
        assert clip_with_video.extension_count == 6
        assert result["extension_count"] == 6


# ── API Endpoint Tests ───────────────────────────────────────────────────────


@pytest.mark.django_db
class TestApiExtendClipEndpoint:
    """Tests for the POST /api/clips/<id>/extend/ endpoint."""

    @patch("core.views.run_in_background")
    def test_returns_202_with_task_id(self, mock_run, api_client, clip_with_video):
        """Successful request should return 202 with task_id."""
        mock_run.return_value = 42

        response = api_client.post(
            f"/api/clips/{clip_with_video.pk}/extend/",
            data=json.dumps({"prompt": "Continue the scene"}),
            content_type="application/json",
        )

        assert response.status_code == 202
        data = response.json()
        assert data["task_id"] == 42
        mock_run.assert_called_once()

    def test_returns_409_when_already_generating(self, api_client, clip_generating):
        """Should return 409 if clip is already generating."""
        response = api_client.post(
            f"/api/clips/{clip_generating.pk}/extend/",
            data=json.dumps({"prompt": "Continue"}),
            content_type="application/json",
        )

        assert response.status_code == 409
        data = response.json()
        assert "already in progress" in data["error"]

    def test_returns_400_when_no_video(self, api_client, clip_no_video):
        """Should return 400 if clip has no video file."""
        response = api_client.post(
            f"/api/clips/{clip_no_video.pk}/extend/",
            data=json.dumps({"prompt": "Continue"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "no generated video" in data["error"]

    def test_returns_400_when_no_reference_id(self, api_client, clip_no_reference):
        """Should return 400 if clip has no generation reference."""
        response = api_client.post(
            f"/api/clips/{clip_no_reference.pk}/extend/",
            data=json.dumps({"prompt": "Continue"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "reference" in data["error"].lower()

    def test_returns_400_when_max_extensions(self, api_client, clip_max_extensions):
        """Should return 400 when max extensions reached."""
        response = api_client.post(
            f"/api/clips/{clip_max_extensions.pk}/extend/",
            data=json.dumps({"prompt": "Continue"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "Maximum extension limit" in data["error"]

    def test_returns_400_when_prompt_empty(self, api_client, clip_with_video):
        """Should return 400 when prompt is empty."""
        response = api_client.post(
            f"/api/clips/{clip_with_video.pk}/extend/",
            data=json.dumps({"prompt": ""}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "prompt is required" in data["error"].lower()

    def test_returns_400_when_prompt_missing(self, api_client, clip_with_video):
        """Should return 400 when prompt key is missing."""
        response = api_client.post(
            f"/api/clips/{clip_with_video.pk}/extend/",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "prompt" in data["error"].lower()

    def test_returns_400_for_invalid_json(self, api_client, clip_with_video):
        """Should return 400 for malformed JSON body."""
        response = api_client.post(
            f"/api/clips/{clip_with_video.pk}/extend/",
            data="not valid json",
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid JSON" in data["error"]

    def test_returns_404_for_nonexistent_clip(self, api_client, db):
        """Should return 404 for a clip ID that does not exist."""
        response = api_client.post(
            "/api/clips/99999/extend/",
            data=json.dumps({"prompt": "Continue"}),
            content_type="application/json",
        )

        assert response.status_code == 404
