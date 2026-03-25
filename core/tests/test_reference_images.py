"""Tests for reference image generation, upload, deletion, and per-clip selection."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from core.models import Clip, Project, ReferenceImage
from core.services.ai_client import reset_client
from core.services.image_generator import generate_reference_image


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
        title="Ref Test Reel",
        description="A reel for testing reference images",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )


@pytest.fixture()
def clip(project):
    """Create a test clip."""
    return Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="A cinematic shot for testing references.",
    )


@pytest.fixture()
def reference_image(project, tmp_path):
    """Create a test reference image with a real file."""
    img_path = tmp_path / "ref_test.png"
    img_path.write_bytes(_make_png_bytes())
    return ReferenceImage.objects.create(
        project=project,
        slot_number=1,
        image_file="images/references/ref_test.png",
        label="Test character",
    )


@pytest.fixture()
def client():
    """Return a Django test client."""
    return Client()


def _make_png_bytes():
    """Return minimal valid PNG bytes for testing."""
    try:
        from PIL import Image

        buf = BytesIO()
        Image.new("RGB", (10, 10), (128, 128, 128)).save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        return (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00"
            b"\x90wS\xde\x00\x00\x00\x0cIDATx"
            b"\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
            b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )


# ── Image Generator Service ────────────────────────────────────────────────


class TestGenerateReferenceImage:
    """Tests for the generate_reference_image service function."""

    @patch("core.services.image_generator.get_ai_client")
    def test_should_return_relative_path_on_success(
        self, mock_client_fn, tmp_path, settings
    ):
        """Generate a reference image and return relative file path."""
        settings.MEDIA_ROOT = str(tmp_path)

        mock_part = MagicMock()
        mock_part.inline_data.data = _make_png_bytes()

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_fn.return_value = mock_client

        result = generate_reference_image("A cat", project_id=42, slot_number=1)

        assert result == "images/references/ref_42_1.png"
        assert (tmp_path / "images" / "references" / "ref_42_1.png").exists()
        mock_client.models.generate_content.assert_called_once()

    @patch("core.services.image_generator.get_ai_client")
    def test_should_raise_on_empty_response(self, mock_client_fn, tmp_path, settings):
        """Raise RuntimeError when API returns no candidates."""
        settings.MEDIA_ROOT = str(tmp_path)

        mock_response = MagicMock()
        mock_response.candidates = []
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_fn.return_value = mock_client

        with pytest.raises(RuntimeError, match="no candidates"):
            generate_reference_image("A cat", project_id=1, slot_number=1)

    @patch("core.services.image_generator.get_ai_client")
    def test_should_raise_on_no_image_data(self, mock_client_fn, tmp_path, settings):
        """Raise RuntimeError when response has no image parts."""
        settings.MEDIA_ROOT = str(tmp_path)

        mock_part = MagicMock()
        mock_part.inline_data = None

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_fn.return_value = mock_client

        with pytest.raises(RuntimeError, match="no image data"):
            generate_reference_image("A cat", project_id=1, slot_number=1)


# ── Upload Endpoint ─────────────────────────────────────────────────────────


class TestUploadReference:
    """Tests for POST /api/projects/<id>/references/upload/."""

    def test_should_upload_image_and_create_record(self, client, project):
        """Upload a valid image file to an empty slot."""
        png = SimpleUploadedFile(
            "char.png", _make_png_bytes(), content_type="image/png"
        )
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "Main character", "image": png},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slot_number"] == 1
        assert data["label"] == "Main character"
        assert ReferenceImage.objects.filter(project=project, slot_number=1).exists()

    def test_should_replace_existing_slot(self, client, project):
        """Uploading to an occupied slot replaces the image."""
        png1 = SimpleUploadedFile("v1.png", _make_png_bytes(), content_type="image/png")
        client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "Version 1", "image": png1},
        )
        png2 = SimpleUploadedFile("v2.png", _make_png_bytes(), content_type="image/png")
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "Version 2", "image": png2},
        )
        assert response.status_code == 201
        assert response.json()["label"] == "Version 2"
        assert (
            ReferenceImage.objects.filter(project=project, slot_number=1).count() == 1
        )

    def test_should_reject_invalid_slot(self, client, project):
        """Return 400 for slot_number outside 1-3."""
        png = SimpleUploadedFile("x.png", _make_png_bytes(), content_type="image/png")
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "5", "label": "Bad", "image": png},
        )
        assert response.status_code == 400

    def test_should_reject_missing_label(self, client, project):
        """Return 400 when label is missing."""
        png = SimpleUploadedFile("x.png", _make_png_bytes(), content_type="image/png")
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "", "image": png},
        )
        assert response.status_code == 400

    def test_should_reject_missing_file(self, client, project):
        """Return 400 when image file is not provided."""
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "Missing file"},
        )
        assert response.status_code == 400

    def test_should_reject_invalid_file_type(self, client, project):
        """Return 400 for unsupported image types."""
        gif = SimpleUploadedFile(
            "anim.gif", b"GIF89a\x01\x00", content_type="image/gif"
        )
        response = client.post(
            f"/api/projects/{project.pk}/references/upload/",
            {"slot_number": "1", "label": "Bad type", "image": gif},
        )
        assert response.status_code == 400


# ── Generate Endpoint ───────────────────────────────────────────────────────


class TestGenerateReference:
    """Tests for POST /api/projects/<id>/references/generate/."""

    def test_should_accept_valid_request(self, client, project):
        """Return 202 with task_id for valid generation request."""
        with patch("core.views.run_in_background", return_value=99):
            response = client.post(
                f"/api/projects/{project.pk}/references/generate/",
                data=json.dumps(
                    {"slot_number": 2, "prompt": "A red car", "label": "Sports car"}
                ),
                content_type="application/json",
            )
        assert response.status_code == 202
        assert response.json()["task_id"] == 99

    def test_should_reject_missing_prompt(self, client, project):
        """Return 400 when prompt is empty."""
        response = client.post(
            f"/api/projects/{project.pk}/references/generate/",
            data=json.dumps({"slot_number": 1, "prompt": "", "label": "X"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_reject_missing_label(self, client, project):
        """Return 400 when label is empty."""
        response = client.post(
            f"/api/projects/{project.pk}/references/generate/",
            data=json.dumps({"slot_number": 1, "prompt": "A thing", "label": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_reject_invalid_slot(self, client, project):
        """Return 400 for slot_number outside 1-3."""
        response = client.post(
            f"/api/projects/{project.pk}/references/generate/",
            data=json.dumps({"slot_number": 0, "prompt": "A thing", "label": "Bad"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_reject_invalid_json(self, client, project):
        """Return 400 for malformed JSON body."""
        response = client.post(
            f"/api/projects/{project.pk}/references/generate/",
            data="not-json",
            content_type="application/json",
        )
        assert response.status_code == 400


# ── Delete Endpoint ─────────────────────────────────────────────────────────


class TestDeleteReference:
    """Tests for POST /api/projects/<id>/references/<slot>/delete/."""

    def test_should_delete_existing_reference(self, client, project):
        """Delete a reference and return success."""
        ReferenceImage.objects.create(
            project=project,
            slot_number=2,
            image_file="images/references/test.png",
            label="To delete",
        )
        response = client.post(
            f"/api/projects/{project.pk}/references/2/delete/",
        )
        assert response.status_code == 200
        assert not ReferenceImage.objects.filter(
            project=project, slot_number=2
        ).exists()

    def test_should_return_404_for_empty_slot(self, client, project):
        """Return 404 when trying to delete an empty slot."""
        response = client.post(
            f"/api/projects/{project.pk}/references/3/delete/",
        )
        assert response.status_code == 404

    def test_should_remove_ref_from_clip_selections(self, client, project):
        """Deleting a reference removes it from clips' selected_references."""
        ref = ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/test.png",
            label="Shared ref",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test clip",
            selected_references=[ref.pk],
        )
        client.post(f"/api/projects/{project.pk}/references/1/delete/")

        clip.refresh_from_db()
        assert ref.pk not in clip.selected_references


# ── Per-Clip Reference Selection ────────────────────────────────────────────


class TestUpdateClipReferences:
    """Tests for POST /api/clips/<id>/update-references/."""

    def test_should_update_selected_references(self, client, project):
        """Save valid reference IDs to the clip."""
        ref1 = ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/r1.png",
            label="Ref 1",
        )
        ref2 = ReferenceImage.objects.create(
            project=project,
            slot_number=2,
            image_file="images/references/r2.png",
            label="Ref 2",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test",
        )

        response = client.post(
            f"/api/clips/{clip.pk}/update-references/",
            data=json.dumps({"reference_ids": [ref1.pk, ref2.pk]}),
            content_type="application/json",
        )
        assert response.status_code == 200
        clip.refresh_from_db()
        assert set(clip.selected_references) == {ref1.pk, ref2.pk}

    def test_should_ignore_invalid_reference_ids(self, client, project):
        """Filter out IDs that do not belong to the project."""
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test",
        )
        response = client.post(
            f"/api/clips/{clip.pk}/update-references/",
            data=json.dumps({"reference_ids": [9999, 8888]}),
            content_type="application/json",
        )
        assert response.status_code == 200
        clip.refresh_from_db()
        assert clip.selected_references == []

    def test_should_reject_non_list(self, client, project):
        """Return 400 when reference_ids is not a list."""
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test",
        )
        response = client.post(
            f"/api/clips/{clip.pk}/update-references/",
            data=json.dumps({"reference_ids": "not-a-list"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_reject_invalid_json(self, client, project):
        """Return 400 for malformed JSON."""
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test",
        )
        response = client.post(
            f"/api/clips/{clip.pk}/update-references/",
            data="invalid",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_clear_references_with_empty_list(self, client, project):
        """Allow clearing all references by passing empty list."""
        ref = ReferenceImage.objects.create(
            project=project,
            slot_number=1,
            image_file="images/references/r.png",
            label="R",
        )
        clip = Clip.objects.create(
            project=project,
            sequence_number=1,
            script_text="Test",
            selected_references=[ref.pk],
        )
        response = client.post(
            f"/api/clips/{clip.pk}/update-references/",
            data=json.dumps({"reference_ids": []}),
            content_type="application/json",
        )
        assert response.status_code == 200
        clip.refresh_from_db()
        assert clip.selected_references == []
