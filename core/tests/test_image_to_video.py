"""Tests for image-to-video generation and first-frame management."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from core.models import Clip, Project
from core.services.ai_client import reset_client
from core.services.video_generator import (
    generate_first_frame_image,
    generate_image_to_video,
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
        title="Image-to-Video Test Reel",
        description="A reel for testing image-to-video generation",
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
        script_text="A cinematic shot of a sunset over the ocean",
        generation_method="image_to_video",
    )


@pytest.fixture()
def clip_with_first_frame(clip, tmp_path):
    """Create a test clip with a first frame image."""
    frame_dir = Path(tmp_path) / "images" / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_file = frame_dir / "test_frame.png"
    frame_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
        clip.first_frame = "images/frames/test_frame.png"
        clip.save(update_fields=["first_frame"])

    return clip


@pytest.fixture()
def clip_no_script(project):
    """Create a test clip without script text."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="",
        generation_method="image_to_video",
    )


@pytest.fixture()
def previous_clip(project, tmp_path):
    """Create a previous clip with a last frame."""
    prev = Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="Previous clip script",
    )
    frame_dir = Path(tmp_path) / "images" / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_file = frame_dir / "last_prev.png"
    frame_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    prev.last_frame = "images/frames/last_prev.png"
    prev.save(update_fields=["last_frame"])
    return prev


@pytest.fixture()
def clip_after_previous(project):
    """Create a clip at sequence 2 for testing previous-clip frame copy."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="Second clip script",
        generation_method="image_to_video",
    )


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


# ── Service Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestGenerateFirstFrameImage:
    """Tests for the generate_first_frame_image service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_generates_and_saves_first_frame(self, mock_get_client, clip, tmp_path):
        """Should generate an image and save it as the clip's first_frame."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_image_part = MagicMock()
        mock_image_part.inline_data.data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_image_part]

        mock_client.models.generate_content.return_value = mock_response

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            result = generate_first_frame_image(clip)

        assert result.startswith("images/frames/")
        assert result.endswith(".png")
        clip.refresh_from_db()
        assert clip.first_frame.name == result

    def test_rejects_empty_script(self, clip_no_script):
        """A clip with no script should raise ValueError."""
        with pytest.raises(ValueError, match="no script text"):
            generate_first_frame_image(clip_no_script)


@pytest.mark.django_db(transaction=True)
class TestGenerateImageToVideo:
    """Tests for the generate_image_to_video service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_successful_generation(self, mock_get_client, clip, tmp_path):
        """Should generate a video using the first frame and script."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        frame_dir = Path(tmp_path) / "images" / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        frame_file = frame_dir / f"first_{clip.project.pk}_{clip.sequence_number}.png"
        frame_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        clip.first_frame = (
            f"images/frames/first_{clip.project.pk}_{clip.sequence_number}.png"
        )
        clip.save(update_fields=["first_frame"])

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/i2v-test-123"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            result = generate_image_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "completed"
        assert clip.generation_reference_id == "operations/i2v-test-123"
        assert result["clip_id"] == clip.pk
        assert "video_url" in result

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs.get("image") is not None

    @patch("core.services.video_generator.get_ai_client")
    def test_handles_api_failure(self, mock_get_client, clip, tmp_path):
        """API failure should set status to failed and raise RuntimeError."""
        frame_dir = Path(tmp_path) / "images" / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        frame_file = frame_dir / "first_frame.png"
        frame_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        clip.first_frame = "images/frames/first_frame.png"
        clip.save(update_fields=["first_frame"])

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_videos.side_effect = Exception("API down")

        with (
            patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)),
            pytest.raises(RuntimeError, match="Image-to-Video generation failed"),
        ):
            generate_image_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"

    def test_rejects_empty_script(self, clip_no_script):
        """A clip with no script should raise ValueError."""
        with pytest.raises(ValueError, match="no script text"):
            generate_image_to_video(clip_no_script)

        clip_no_script.refresh_from_db()
        assert clip_no_script.generation_status == "failed"

    def test_rejects_missing_first_frame(self, clip):
        """A clip with no first_frame should raise ValueError."""
        clip.first_frame = ""
        clip.save(update_fields=["first_frame"])

        with pytest.raises(ValueError, match="no first frame"):
            generate_image_to_video(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"


# ── Endpoint Tests ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSetFirstFrameEndpoint:
    """Tests for POST /api/clips/<id>/set-first-frame/."""

    def test_generate_returns_202(self, api_client, clip):
        """POST with source=generate should return 202 with task_id."""
        with patch("core.views.run_in_background", return_value=42):
            response = api_client.post(
                f"/api/clips/{clip.pk}/set-first-frame/",
                data=json.dumps({"source": "generate"}),
                content_type="application/json",
            )

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data

    def test_generate_rejects_empty_script(self, api_client, clip_no_script):
        """POST with source=generate on scriptless clip returns 400."""
        response = api_client.post(
            f"/api/clips/{clip_no_script.pk}/set-first-frame/",
            data=json.dumps({"source": "generate"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "script" in response.json()["error"].lower()

    def test_upload_sets_first_frame(self, api_client, clip):
        """Multipart upload should save the image as first_frame."""
        image = SimpleUploadedFile(
            "test_frame.png",
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
            content_type="image/png",
        )

        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data={"source": "upload", "image": image},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "set"
        assert "image_url" in data

        clip.refresh_from_db()
        assert clip.first_frame.name != ""

    def test_upload_rejects_missing_file(self, api_client, clip):
        """Multipart upload without file returns 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data={"source": "upload"},
        )

        assert response.status_code == 400
        assert "image" in response.json()["error"].lower()

    def test_upload_rejects_invalid_type(self, api_client, clip):
        """Multipart upload with non-image file returns 400."""
        bad_file = SimpleUploadedFile(
            "script.txt",
            b"not an image",
            content_type="text/plain",
        )

        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data={"source": "upload", "image": bad_file},
        )

        assert response.status_code == 400
        assert "JPEG, PNG, or WebP" in response.json()["error"]

    def test_previous_clip_copies_last_frame(
        self, api_client, previous_clip, clip_after_previous, tmp_path
    ):
        """POST with source=previous_clip should copy the last frame."""
        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            response = api_client.post(
                f"/api/clips/{clip_after_previous.pk}/set-first-frame/",
                data=json.dumps({"source": "previous_clip"}),
                content_type="application/json",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "set"

        clip_after_previous.refresh_from_db()
        assert clip_after_previous.first_frame.name != ""

    def test_previous_clip_rejects_clip_1(self, api_client, clip):
        """Clip 1 has no previous clip — should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data=json.dumps({"source": "previous_clip"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "previous" in response.json()["error"].lower()

    def test_invalid_source_returns_400(self, api_client, clip):
        """Invalid source value should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data=json.dumps({"source": "invalid"}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_invalid_json_returns_400(self, api_client, clip):
        """Malformed JSON should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-first-frame/",
            data="not json",
            content_type="application/json",
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestUpdateGenerationMethodEndpoint:
    """Tests for POST /api/clips/<id>/update-method/."""

    def test_updates_method(self, api_client, clip):
        """Should update the generation method and return 200."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/update-method/",
            data=json.dumps({"method": "text_to_video"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        clip.refresh_from_db()
        assert clip.generation_method == "text_to_video"

    def test_rejects_invalid_method(self, api_client, clip):
        """Invalid method name should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/update-method/",
            data=json.dumps({"method": "nonexistent"}),
            content_type="application/json",
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestGenerateVideoDispatch:
    """Tests for generate-video endpoint with method dispatch."""

    def test_dispatches_text_to_video(self, api_client, clip):
        """Default method should dispatch to text_to_video generator."""
        clip.generation_method = "text_to_video"
        clip.save(update_fields=["generation_method"])

        with patch("core.views.run_in_background", return_value=1) as mock_run:
            response = api_client.post(
                f"/api/clips/{clip.pk}/generate-video/",
                data=json.dumps({"method": "text_to_video"}),
                content_type="application/json",
            )

        assert response.status_code == 202
        mock_run.assert_called_once()

    def test_dispatches_image_to_video(self, api_client, clip):
        """Image-to-video method requires first_frame set."""
        clip.first_frame = "images/frames/test.png"
        clip.save(update_fields=["first_frame"])

        with patch("core.views.run_in_background", return_value=2):
            response = api_client.post(
                f"/api/clips/{clip.pk}/generate-video/",
                data=json.dumps({"method": "image_to_video"}),
                content_type="application/json",
            )

        assert response.status_code == 202

    def test_image_to_video_rejects_no_first_frame(self, api_client, clip):
        """Image-to-video without first_frame should return 400."""
        clip.first_frame = ""
        clip.save(update_fields=["first_frame"])

        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "image_to_video"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "first frame" in response.json()["error"].lower()

    def test_unknown_method_returns_400(self, api_client, clip):
        """Unknown generation method should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "unknown_method"}),
            content_type="application/json",
        )

        assert response.status_code == 400
