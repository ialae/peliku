"""Tests for script regeneration API endpoints (single clip and full)."""

from unittest.mock import patch

import pytest

from django.test import Client

from core.models import Clip, Project
from core.services.ai_client import reset_client


@pytest.fixture(autouse=True)
def _reset_ai_client():
    """Reset the AI client singleton before each test."""
    reset_client()
    yield
    reset_client()


@pytest.fixture()
def project(db):
    """Create a test project with 5 clips."""
    proj = Project.objects.create(
        title="Regen Test Reel",
        description="A reel for testing script regeneration",
        visual_style="Cinematic, dark tones",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=5,
    )
    for i in range(1, 6):
        Clip.objects.create(
            project=proj,
            sequence_number=i,
            script_text=f"Original script for clip {i}",
        )
    return proj


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


@pytest.mark.django_db
class TestRegenerateSingleScript:
    """Tests for POST /api/clips/<id>/regenerate-script/."""

    @patch("core.views.regenerate_single_script")
    def test_returns_new_script_on_success(self, mock_regen, api_client, project):
        clip = project.clips.first()
        mock_regen.return_value = "Brand new regenerated script"

        response = api_client.post(
            f"/api/clips/{clip.pk}/regenerate-script/",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "regenerated"
        assert data["clip_id"] == clip.pk
        assert data["script_text"] == "Brand new regenerated script"

    @patch("core.views.regenerate_single_script")
    def test_persists_new_script_to_database(self, mock_regen, api_client, project):
        clip = project.clips.first()
        mock_regen.return_value = "Saved regenerated script"

        api_client.post(
            f"/api/clips/{clip.pk}/regenerate-script/",
            content_type="application/json",
        )

        clip.refresh_from_db()
        assert clip.script_text == "Saved regenerated script"

    @patch("core.views.regenerate_single_script")
    def test_calls_service_with_correct_clip(self, mock_regen, api_client, project):
        clip = project.clips.order_by("sequence_number")[2]
        mock_regen.return_value = "New clip 3 script"

        api_client.post(
            f"/api/clips/{clip.pk}/regenerate-script/",
            content_type="application/json",
        )

        mock_regen.assert_called_once()
        called_clip = mock_regen.call_args[0][0]
        assert called_clip.pk == clip.pk

    @patch("core.views.regenerate_single_script")
    def test_returns_500_on_service_failure(self, mock_regen, api_client, project):
        clip = project.clips.first()
        mock_regen.side_effect = Exception("Gemini API error")

        response = api_client.post(
            f"/api/clips/{clip.pk}/regenerate-script/",
            content_type="application/json",
        )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data

    def test_returns_404_for_nonexistent_clip(self, api_client):
        response = api_client.post(
            "/api/clips/99999/regenerate-script/",
            content_type="application/json",
        )

        assert response.status_code == 404

    @patch("core.views.regenerate_single_script")
    def test_does_not_affect_other_clips(self, mock_regen, api_client, project):
        clip = project.clips.order_by("sequence_number").first()
        other_clip = project.clips.order_by("sequence_number")[1]
        original_other_text = other_clip.script_text
        mock_regen.return_value = "Changed script"

        api_client.post(
            f"/api/clips/{clip.pk}/regenerate-script/",
            content_type="application/json",
        )

        other_clip.refresh_from_db()
        assert other_clip.script_text == original_other_text

    def test_rejects_get_method(self, api_client, project):
        clip = project.clips.first()

        response = api_client.get(
            f"/api/clips/{clip.pk}/regenerate-script/",
        )

        assert response.status_code == 405


@pytest.mark.django_db
class TestRegenerateAllScripts:
    """Tests for POST /api/projects/<id>/regenerate-all-scripts/."""

    @patch("core.views.regenerate_all_scripts")
    def test_returns_all_new_scripts_on_success(
        self, mock_regen_all, api_client, project
    ):
        new_scripts = [f"New script {i}" for i in range(1, 6)]
        mock_regen_all.return_value = new_scripts

        response = api_client.post(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "regenerated"
        assert len(data["scripts"]) == 5
        for i, script_info in enumerate(data["scripts"]):
            assert script_info["script_text"] == f"New script {i + 1}"
            assert script_info["sequence_number"] == i + 1

    @patch("core.views.regenerate_all_scripts")
    def test_persists_all_new_scripts_to_database(
        self, mock_regen_all, api_client, project
    ):
        new_scripts = [f"Persisted script {i}" for i in range(1, 6)]
        mock_regen_all.return_value = new_scripts

        api_client.post(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        clips = project.clips.order_by("sequence_number")
        for i, clip in enumerate(clips):
            assert clip.script_text == f"Persisted script {i + 1}"

    @patch("core.views.regenerate_all_scripts")
    def test_calls_service_with_correct_project(
        self, mock_regen_all, api_client, project
    ):
        mock_regen_all.return_value = ["s"] * 5

        api_client.post(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        mock_regen_all.assert_called_once()
        called_project = mock_regen_all.call_args[0][0]
        assert called_project.pk == project.pk

    @patch("core.views.regenerate_all_scripts")
    def test_returns_500_on_service_failure(self, mock_regen_all, api_client, project):
        mock_regen_all.side_effect = Exception("Gemini API error")

        response = api_client.post(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data

    def test_returns_404_for_nonexistent_project(self, api_client):
        response = api_client.post(
            "/api/projects/99999/regenerate-all-scripts/",
            content_type="application/json",
        )

        assert response.status_code == 404

    @patch("core.views.regenerate_all_scripts")
    def test_returns_400_for_project_with_no_clips(
        self, mock_regen_all, api_client, db
    ):
        empty_project = Project.objects.create(
            title="Empty Project",
            description="No clips here",
            aspect_ratio="9:16",
            clip_duration=8,
            num_clips=5,
        )

        response = api_client.post(
            f"/api/projects/{empty_project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        mock_regen_all.assert_not_called()

    def test_rejects_get_method(self, api_client, project):
        response = api_client.get(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
        )

        assert response.status_code == 405

    @patch("core.views.regenerate_all_scripts")
    def test_preserves_clip_order_in_response(
        self, mock_regen_all, api_client, project
    ):
        new_scripts = [f"Ordered script {i}" for i in range(1, 6)]
        mock_regen_all.return_value = new_scripts

        response = api_client.post(
            f"/api/projects/{project.pk}/regenerate-all-scripts/",
            content_type="application/json",
        )

        data = response.json()
        sequence_numbers = [s["sequence_number"] for s in data["scripts"]]
        assert sequence_numbers == [1, 2, 3, 4, 5]
