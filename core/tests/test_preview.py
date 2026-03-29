"""Tests for the reel preview data endpoint and clip ordering."""

import pytest

from django.test import Client

from core.models import Clip, Hook, Project


@pytest.fixture()
def project(db):
    """Create a test project with 3 clips."""
    proj = Project.objects.create(
        title="Preview Test Reel",
        description="Testing the preview data endpoint",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )
    Clip.objects.create(project=proj, sequence_number=1, script_text="Clip one")
    Clip.objects.create(project=proj, sequence_number=2, script_text="Clip two")
    Clip.objects.create(project=proj, sequence_number=3, script_text="Clip three")
    return proj


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


@pytest.mark.django_db
class TestPreviewDataEndpoint:
    """Tests for GET /api/projects/<id>/preview-data/."""

    def test_returns_200_for_existing_project(self, api_client, project):
        """Should return HTTP 200 with JSON clip data."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert "clips" in data
        assert "hook" in data
        assert "aspect_ratio" in data

    def test_returns_404_for_nonexistent_project(self, api_client, db):
        """Should return 404 for a missing project."""
        response = api_client.get("/api/projects/99999/preview-data/")
        assert response.status_code == 404

    def test_clips_ordered_by_sequence_number(self, api_client, project):
        """Should return clips in sequence_number order."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        clips = data["clips"]
        assert len(clips) == 3
        assert clips[0]["sequence_number"] == 1
        assert clips[1]["sequence_number"] == 2
        assert clips[2]["sequence_number"] == 3

    def test_clip_video_url_null_when_no_video(self, api_client, project):
        """Should return null video_url for clips without generated video."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        for clip in data["clips"]:
            assert clip["video_url"] is None

    def test_clip_video_url_present_when_video_exists(self, api_client, project):
        """Should return a video_url when clip has a video file."""
        clip = project.clips.get(sequence_number=1)
        clip.video_file = "videos/test_clip.mp4"
        clip.save(update_fields=["video_file"])

        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["clips"][0]["video_url"] is not None
        assert "test_clip.mp4" in data["clips"][0]["video_url"]

    def test_clips_include_duration(self, api_client, project):
        """Should include the project clip_duration for each clip."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        for clip in data["clips"]:
            assert clip["duration"] == 8

    def test_aspect_ratio_returned(self, api_client, project):
        """Should return the project's aspect ratio."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["aspect_ratio"] == "9:16"

    def test_hook_null_when_no_hook_exists(self, api_client, project):
        """Should return null hook when project has no hook."""
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["hook"] is None

    def test_hook_data_when_hook_exists(self, api_client, project):
        """Should return hook data when project has a hook."""
        Hook.objects.create(
            project=project,
            script_text="Attention grabber",
            is_enabled=True,
        )
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["hook"] is not None
        assert data["hook"]["is_enabled"] is True
        assert data["hook"]["duration"] == 4
        assert data["hook"]["video_url"] is None

    def test_hook_with_video(self, api_client, project):
        """Should return hook video_url when hook has a video."""
        Hook.objects.create(
            project=project,
            script_text="Hook script",
            video_file="videos/hooks/hook_test.mp4",
            is_enabled=True,
        )
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["hook"]["video_url"] is not None
        assert "hook_test.mp4" in data["hook"]["video_url"]

    def test_hook_disabled(self, api_client, project):
        """Should return is_enabled=False when hook is disabled."""
        Hook.objects.create(
            project=project,
            script_text="Hook script",
            is_enabled=False,
        )
        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["hook"]["is_enabled"] is False


@pytest.mark.django_db
class TestPreviewDataClipOrdering:
    """Tests for clip ordering in the preview data response."""

    def test_clips_respect_sequence_after_reorder(self, api_client):
        """Should return clips in updated sequence order."""
        project = Project.objects.create(
            title="Reordered Preview",
            description="Test reorder",
            aspect_ratio="16:9",
            clip_duration=6,
            num_clips=3,
        )
        Clip.objects.create(project=project, sequence_number=1, script_text="Was first")
        Clip.objects.create(
            project=project, sequence_number=2, script_text="Was second"
        )
        Clip.objects.create(project=project, sequence_number=3, script_text="Was third")

        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()

        sequence_numbers = [c["sequence_number"] for c in data["clips"]]
        assert sequence_numbers == [1, 2, 3]

    def test_landscape_aspect_ratio(self, api_client):
        """Should return 16:9 aspect ratio for landscape projects."""
        project = Project.objects.create(
            title="Landscape Preview",
            description="Test landscape",
            aspect_ratio="16:9",
            clip_duration=6,
            num_clips=2,
        )
        Clip.objects.create(project=project, sequence_number=1, script_text="Scene one")
        Clip.objects.create(project=project, sequence_number=2, script_text="Scene two")

        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["aspect_ratio"] == "16:9"
        assert len(data["clips"]) == 2

    def test_clips_include_correct_ids(self, api_client):
        """Should include correct clip IDs in the response."""
        project = Project.objects.create(
            title="ID Test",
            description="Test IDs",
            aspect_ratio="9:16",
            clip_duration=8,
            num_clips=2,
        )
        clip1 = Clip.objects.create(
            project=project, sequence_number=1, script_text="First"
        )
        clip2 = Clip.objects.create(
            project=project, sequence_number=2, script_text="Second"
        )

        url = f"/api/projects/{project.pk}/preview-data/"
        response = api_client.get(url)
        data = response.json()
        assert data["clips"][0]["id"] == clip1.pk
        assert data["clips"][1]["id"] == clip2.pk
