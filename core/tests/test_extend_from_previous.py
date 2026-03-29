"""Tests for the Extend from Previous Clip generation method."""

import json
from unittest.mock import MagicMock, patch

import pytest

from django.test import Client

from core.models import Clip, Project
from core.services.ai_client import reset_client
from core.services.video_generator import generate_extend_from_previous


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
        title="Extend Previous Test Reel",
        description="A reel for testing extend from previous clip",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=5,
    )


@pytest.fixture()
def clip_1_with_video(project):
    """Clip 1 with a completed video and generation reference."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="A cinematic opening scene",
        video_file="videos/clip_1_1.mp4",
        generation_status="completed",
        generation_reference_id="operations/prev-ref-001",
    )


@pytest.fixture()
def clip_2(project, clip_1_with_video):
    """Clip 2 ready for extend from previous."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="The camera pans to reveal a hidden garden",
    )


@pytest.fixture()
def clip_1_no_video(project):
    """Clip 1 without a generated video."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="Scene description",
        generation_status="idle",
    )


@pytest.fixture()
def clip_2_no_prev_video(project, clip_1_no_video):
    """Clip 2 where previous clip has no video."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="Next scene description",
    )


@pytest.fixture()
def clip_1_no_reference(project):
    """Clip 1 with video but no generation reference ID."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="Scene with video",
        video_file="videos/clip_1_1.mp4",
        generation_status="completed",
        generation_reference_id="",
    )


@pytest.fixture()
def clip_2_no_prev_ref(project, clip_1_no_reference):
    """Clip 2 where previous clip has no generation reference."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="Next scene script",
    )


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


# ── Service Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestGenerateExtendFromPreviousService:
    """Tests for the generate_extend_from_previous service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_successful_extend_from_previous(self, mock_get_client, clip_2, tmp_path):
        """Should generate video by extending previous clip."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/ext-prev-001"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.files.download = MagicMock()

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
            result = generate_extend_from_previous(clip_2)

        clip_2.refresh_from_db()
        assert clip_2.generation_status == "completed"
        assert clip_2.generation_reference_id == "operations/ext-prev-001"
        assert "video_url" in result
        assert result["clip_id"] == clip_2.pk

    @patch("core.services.video_generator.get_ai_client")
    def test_calls_veo_with_previous_clip_reference(
        self, mock_get_client, clip_2, tmp_path
    ):
        """Should pass the previous clip's generation reference to Veo."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/ext-prev-002"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.files.download = MagicMock()

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
            generate_extend_from_previous(clip_2)

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs["video"].uri == "operations/prev-ref-001"
        assert call_kwargs.kwargs["prompt"] == clip_2.script_text.strip()

    @patch("core.services.video_generator.get_ai_client")
    def test_resolution_locked_to_720p(self, mock_get_client, clip_2, tmp_path):
        """Should send resolution 720p in the config."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/ext-prev-003"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.files.download = MagicMock()

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
            generate_extend_from_previous(clip_2)

        call_kwargs = mock_client.models.generate_videos.call_args
        config = call_kwargs.kwargs["config"]
        assert config.resolution == "720p"

    def test_raises_for_clip_1(self, project):
        """Should raise ValueError for Clip 1 (no previous clip)."""
        clip_1 = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="First clip",
        )
        with pytest.raises(ValueError, match="not available for Clip 1"):
            generate_extend_from_previous(clip_1)

        clip_1.refresh_from_db()
        assert clip_1.generation_status == "failed"

    def test_raises_when_previous_clip_has_no_video(self, clip_2_no_prev_video):
        """Should raise ValueError when previous clip has no video."""
        with pytest.raises(ValueError, match="no generated video"):
            generate_extend_from_previous(clip_2_no_prev_video)

        clip_2_no_prev_video.refresh_from_db()
        assert clip_2_no_prev_video.generation_status == "failed"

    def test_raises_when_previous_clip_has_no_reference(self, clip_2_no_prev_ref):
        """Should raise ValueError when previous clip has no reference ID."""
        with pytest.raises(ValueError, match="no generation reference ID"):
            generate_extend_from_previous(clip_2_no_prev_ref)

        clip_2_no_prev_ref.refresh_from_db()
        assert clip_2_no_prev_ref.generation_status == "failed"

    def test_raises_when_no_script_text(self, project):
        """Should raise ValueError when clip has empty script."""
        Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Previous scene",
            video_file="videos/clip_1_1.mp4",
            generation_status="completed",
            generation_reference_id="operations/ref-001",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=2,
            script_text="",
        )
        with pytest.raises(ValueError, match="no script text"):
            generate_extend_from_previous(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"

    @patch("core.services.video_generator.get_ai_client")
    def test_sets_status_to_failed_on_api_error(self, mock_get_client, clip_2):
        """Should set status to 'failed' when the API call raises."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_videos.side_effect = RuntimeError("API down")

        with pytest.raises(RuntimeError, match="Extend from Previous"):
            generate_extend_from_previous(clip_2)

        clip_2.refresh_from_db()
        assert clip_2.generation_status == "failed"


# ── API Endpoint Tests ───────────────────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestExtendPreviousEndpoint:
    """Tests for POST /api/clips/<id>/generate-video/ with extend_previous."""

    def test_accepts_extend_previous_method(self, api_client, clip_2):
        """Should accept extend_previous and return 202 with task_id."""
        with patch("core.views.run_in_background", return_value=42):
            response = api_client.post(
                f"/api/clips/{clip_2.pk}/generate-video/",
                data=json.dumps({"method": "extend_previous"}),
                content_type="application/json",
            )

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data

    def test_rejects_extend_previous_for_clip_1(self, api_client, project):
        """Should return 400 for Clip 1 with extend_previous method."""
        clip_1 = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="First clip script",
        )
        response = api_client.post(
            f"/api/clips/{clip_1.pk}/generate-video/",
            data=json.dumps({"method": "extend_previous"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "not available for Clip 1" in data["error"]

    def test_rejects_when_previous_clip_no_video(
        self, api_client, clip_2_no_prev_video
    ):
        """Should return 400 when previous clip has no video."""
        response = api_client.post(
            f"/api/clips/{clip_2_no_prev_video.pk}/generate-video/",
            data=json.dumps({"method": "extend_previous"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "no generated video" in data["error"]

    def test_rejects_when_previous_clip_no_reference(
        self, api_client, clip_2_no_prev_ref
    ):
        """Should return 400 when previous clip has no reference."""
        response = api_client.post(
            f"/api/clips/{clip_2_no_prev_ref.pk}/generate-video/",
            data=json.dumps({"method": "extend_previous"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "no generation reference" in data["error"]

    def test_rejects_clip_already_generating(self, api_client, project):
        """Should return 409 when clip is already generating."""
        Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Prev",
            video_file="videos/clip_1_1.mp4",
            generation_status="completed",
            generation_reference_id="operations/ref-001",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=2,
            script_text="Current",
            generation_status="generating",
        )
        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "extend_previous"}),
            content_type="application/json",
        )

        assert response.status_code == 409

    def test_rejects_clip_with_no_script(self, api_client, project):
        """Should return 400 when clip has no script text."""
        Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Prev scene",
            video_file="videos/clip_1_1.mp4",
            generation_status="completed",
            generation_reference_id="operations/ref-001",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=2,
            script_text="",
        )
        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "extend_previous"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "no script text" in data["error"].lower()
