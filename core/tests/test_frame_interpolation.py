"""Tests for Frame Interpolation generation and last-frame management."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from core.models import Clip, Project
from core.services.ai_client import reset_client
from core.services.video_generator import (
    generate_frame_interpolation,
    generate_last_frame_image,
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
        title="Frame Interpolation Test Reel",
        description="A reel for testing frame interpolation generation",
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
        generation_method="frame_interpolation",
    )


@pytest.fixture()
def clip_with_frames(clip, tmp_path):
    """Create a test clip with both first and last frame images."""
    frame_dir = Path(tmp_path) / "images" / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    first_file = frame_dir / "test_first.png"
    first_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    last_file = frame_dir / "test_last.png"
    last_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
        clip.first_frame = "images/frames/test_first.png"
        clip.last_frame = "images/frames/test_last.png"
        clip.save(update_fields=["first_frame", "last_frame"])

    return clip


@pytest.fixture()
def clip_no_script(project):
    """Create a test clip without script text."""
    return Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="",
        generation_method="frame_interpolation",
    )


@pytest.fixture()
def next_clip(project, tmp_path):
    """Create a next clip with a first frame."""
    nxt = Clip.objects.create(
        project=project,
        sequence_number=2,
        script_text="Next clip script",
    )
    frame_dir = Path(tmp_path) / "images" / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_file = frame_dir / "first_next.png"
    frame_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    nxt.first_frame = "images/frames/first_next.png"
    nxt.save(update_fields=["first_frame"])
    return nxt


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


# ── Service Tests: generate_last_frame_image ─────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestGenerateLastFrameImage:
    """Tests for the generate_last_frame_image service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_generates_and_saves_last_frame(self, mock_get_client, clip, tmp_path):
        """Should generate an image and save it as the clip's last_frame."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_image_part = MagicMock()
        mock_image_part.inline_data.data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_image_part]

        mock_client.models.generate_content.return_value = mock_response

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            result = generate_last_frame_image(clip)

        assert result.startswith("images/frames/")
        assert result.endswith(".png")
        clip.refresh_from_db()
        assert clip.last_frame.name == result

    def test_rejects_empty_script(self, clip_no_script):
        """A clip with no script should raise ValueError."""
        with pytest.raises(ValueError, match="no script text"):
            generate_last_frame_image(clip_no_script)


# ── Service Tests: generate_frame_interpolation ──────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestGenerateFrameInterpolation:
    """Tests for the generate_frame_interpolation service function."""

    @patch("core.services.video_generator.get_ai_client")
    def test_successful_generation(self, mock_get_client, clip, tmp_path):
        """Should generate a video using both first and last frames."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        frame_dir = Path(tmp_path) / "images" / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)

        first_file = frame_dir / f"first_{clip.project.pk}_{clip.sequence_number}.png"
        first_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        clip.first_frame = (
            f"images/frames/first_{clip.project.pk}_{clip.sequence_number}.png"
        )

        last_file = frame_dir / f"last_{clip.project.pk}_{clip.sequence_number}.png"
        last_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        clip.last_frame = (
            f"images/frames/last_{clip.project.pk}_{clip.sequence_number}.png"
        )
        clip.save(update_fields=["first_frame", "last_frame"])

        mock_video = MagicMock()
        mock_video.video = MagicMock()
        mock_video.video.save = MagicMock()

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/fi-test-123"
        mock_operation.response.generated_videos = [mock_video]

        mock_client.models.generate_videos.return_value = mock_operation

        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            result = generate_frame_interpolation(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "completed"
        assert clip.generation_reference_id == "operations/fi-test-123"
        assert result["clip_id"] == clip.pk
        assert "video_url" in result

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs.get("image") is not None
        assert call_kwargs.kwargs.get("end_image") is not None

    @patch("core.services.video_generator.get_ai_client")
    def test_handles_api_failure(self, mock_get_client, clip, tmp_path):
        """API failure should set status to failed and raise RuntimeError."""
        frame_dir = Path(tmp_path) / "images" / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)

        first_file = frame_dir / "first_frame.png"
        first_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        clip.first_frame = "images/frames/first_frame.png"

        last_file = frame_dir / "last_frame.png"
        last_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        clip.last_frame = "images/frames/last_frame.png"
        clip.save(update_fields=["first_frame", "last_frame"])

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_videos.side_effect = Exception("API down")

        with (
            patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)),
            pytest.raises(RuntimeError, match="Frame Interpolation generation failed"),
        ):
            generate_frame_interpolation(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"

    def test_rejects_empty_script(self, clip_no_script):
        """A clip with no script should raise ValueError."""
        with pytest.raises(ValueError, match="no script text"):
            generate_frame_interpolation(clip_no_script)

        clip_no_script.refresh_from_db()
        assert clip_no_script.generation_status == "failed"

    def test_rejects_missing_first_frame(self, clip):
        """A clip with no first_frame should raise ValueError."""
        clip.first_frame = ""
        clip.last_frame = "images/frames/some_last.png"
        clip.save(update_fields=["first_frame", "last_frame"])

        with pytest.raises(ValueError, match="no first frame"):
            generate_frame_interpolation(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"

    def test_rejects_missing_last_frame(self, clip):
        """A clip with no last_frame should raise ValueError."""
        clip.first_frame = "images/frames/some_first.png"
        clip.last_frame = ""
        clip.save(update_fields=["first_frame", "last_frame"])

        with pytest.raises(ValueError, match="no last frame"):
            generate_frame_interpolation(clip)

        clip.refresh_from_db()
        assert clip.generation_status == "failed"


# ── Endpoint Tests: set-last-frame ───────────────────────────────────────────


@pytest.mark.django_db
class TestSetLastFrameEndpoint:
    """Tests for POST /api/clips/<id>/set-last-frame/."""

    def test_generate_returns_202(self, api_client, clip):
        """POST with source=generate should return 202 with task_id."""
        with patch("core.views.run_in_background", return_value=42):
            response = api_client.post(
                f"/api/clips/{clip.pk}/set-last-frame/",
                data=json.dumps({"source": "generate"}),
                content_type="application/json",
            )

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data

    def test_generate_rejects_empty_script(self, api_client, clip_no_script):
        """POST with source=generate on scriptless clip returns 400."""
        response = api_client.post(
            f"/api/clips/{clip_no_script.pk}/set-last-frame/",
            data=json.dumps({"source": "generate"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "script" in response.json()["error"].lower()

    def test_upload_sets_last_frame(self, api_client, clip):
        """Multipart upload should save the image as last_frame."""
        image = SimpleUploadedFile(
            "test_last_frame.png",
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
            content_type="image/png",
        )

        response = api_client.post(
            f"/api/clips/{clip.pk}/set-last-frame/",
            data={"source": "upload", "image": image},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "set"
        assert "image_url" in data

        clip.refresh_from_db()
        assert clip.last_frame.name != ""

    def test_upload_rejects_missing_file(self, api_client, clip):
        """Multipart upload without file returns 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-last-frame/",
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
            f"/api/clips/{clip.pk}/set-last-frame/",
            data={"source": "upload", "image": bad_file},
        )

        assert response.status_code == 400
        assert "JPEG, PNG, or WebP" in response.json()["error"]

    def test_next_clip_copies_first_frame(self, api_client, clip, next_clip, tmp_path):
        """POST with source=next_clip should copy the first frame."""
        with patch("django.conf.settings.MEDIA_ROOT", str(tmp_path)):
            response = api_client.post(
                f"/api/clips/{clip.pk}/set-last-frame/",
                data=json.dumps({"source": "next_clip"}),
                content_type="application/json",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "set"

        clip.refresh_from_db()
        assert clip.last_frame.name != ""

    def test_next_clip_rejects_when_no_next(self, api_client, clip):
        """Last clip has no next clip — should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-last-frame/",
            data=json.dumps({"source": "next_clip"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "next" in response.json()["error"].lower()

    def test_invalid_source_returns_400(self, api_client, clip):
        """Invalid source value should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-last-frame/",
            data=json.dumps({"source": "invalid"}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_invalid_json_returns_400(self, api_client, clip):
        """Malformed JSON should return 400."""
        response = api_client.post(
            f"/api/clips/{clip.pk}/set-last-frame/",
            data="not json",
            content_type="application/json",
        )

        assert response.status_code == 400


# ── Endpoint Tests: generate-video with frame_interpolation ──────────────────


@pytest.mark.django_db
class TestGenerateVideoFrameInterpolation:
    """Tests for generate-video endpoint with frame_interpolation method."""

    def test_dispatches_frame_interpolation(self, api_client, clip_with_frames):
        """Should dispatch to frame_interpolation generator."""
        with patch("core.views.run_in_background", return_value=1) as mock_run:
            response = api_client.post(
                f"/api/clips/{clip_with_frames.pk}/generate-video/",
                data=json.dumps({"method": "frame_interpolation"}),
                content_type="application/json",
            )

        assert response.status_code == 202
        assert mock_run.called
        func_used = mock_run.call_args[0][1]
        assert func_used is generate_frame_interpolation

    def test_rejects_missing_first_frame(self, api_client, clip):
        """Frame Interpolation without first frame should return 400."""
        clip.first_frame = ""
        clip.last_frame = "images/frames/some_last.png"
        clip.save(update_fields=["first_frame", "last_frame"])

        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "frame_interpolation"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "first frame" in response.json()["error"].lower()

    def test_rejects_missing_last_frame(self, api_client, clip):
        """Frame Interpolation without last frame should return 400."""
        clip.first_frame = "images/frames/some_first.png"
        clip.last_frame = ""
        clip.save(update_fields=["first_frame", "last_frame"])

        response = api_client.post(
            f"/api/clips/{clip.pk}/generate-video/",
            data=json.dumps({"method": "frame_interpolation"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "last frame" in response.json()["error"].lower()
