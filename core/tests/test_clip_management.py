"""Tests for clip management: reorder, add, and delete API endpoints."""

import json

import pytest

from django.test import Client

from core.models import Clip, Project


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def project_with_clips(db):
    """Create a project with 3 clips at consecutive sequence numbers."""
    project = Project.objects.create(
        title="Clip Test Project",
        description="Project for clip management tests.",
        visual_style="Cinematic tones",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )
    for seq in range(1, 4):
        Clip.objects.create(
            project=project,
            sequence_number=seq,
            script_text=f"Script for clip {seq}",
        )
    return project


@pytest.fixture
def project_with_one_clip(db):
    """Create a project with exactly one clip (minimum)."""
    project = Project.objects.create(
        title="Single Clip Project",
        description="Project with one clip.",
        num_clips=1,
    )
    Clip.objects.create(
        project=project,
        sequence_number=1,
        script_text="Only clip",
    )
    return project


@pytest.fixture
def project_at_max_clips(db):
    """Create a project with 10 clips (the maximum)."""
    project = Project.objects.create(
        title="Full Project",
        description="Project at max clips.",
        num_clips=10,
    )
    for seq in range(1, 11):
        Clip.objects.create(
            project=project,
            sequence_number=seq,
            script_text=f"Script for clip {seq}",
        )
    return project


@pytest.mark.django_db
class TestReorderClips:
    """Verify clip reorder API endpoint."""

    def test_reorder_reverses_order(self, client, project_with_clips):
        """Should reverse the clip sequence when IDs are sent in reverse."""
        project = project_with_clips
        clips = list(project.clips.order_by("sequence_number"))
        reversed_ids = [c.pk for c in reversed(clips)]

        response = client.post(
            f"/api/projects/{project.pk}/clips/reorder/",
            data=json.dumps({"clip_ids": reversed_ids}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reordered"

        for clip in clips:
            clip.refresh_from_db()

        assert clips[0].sequence_number == 3
        assert clips[1].sequence_number == 2
        assert clips[2].sequence_number == 1

    def test_reorder_rejects_invalid_json(self, client, project_with_clips):
        """Should return 400 when request body is not valid JSON."""
        response = client.post(
            f"/api/projects/{project_with_clips.pk}/clips/reorder/",
            data="not json",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["error"]

    def test_reorder_rejects_missing_clip_ids(self, client, project_with_clips):
        """Should return 400 when clip_ids key is missing."""
        response = client.post(
            f"/api/projects/{project_with_clips.pk}/clips/reorder/",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "clip_ids must be a list" in response.json()["error"]

    def test_reorder_rejects_mismatched_ids(self, client, project_with_clips):
        """Should return 400 when clip_ids do not match project clips."""
        response = client.post(
            f"/api/projects/{project_with_clips.pk}/clips/reorder/",
            data=json.dumps({"clip_ids": [99999, 88888, 77777]}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "exactly all clip IDs" in response.json()["error"]

    def test_reorder_rejects_duplicate_ids(self, client, project_with_clips):
        """Should return 400 when clip_ids contains duplicates."""
        project = project_with_clips
        clips = list(project.clips.order_by("sequence_number"))
        # Send correct set of IDs but with a duplicate replacing one
        duplicate_ids = [clips[0].pk, clips[0].pk, clips[2].pk]

        response = client.post(
            f"/api/projects/{project.pk}/clips/reorder/",
            data=json.dumps({"clip_ids": duplicate_ids}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_reorder_returns_404_for_missing_project(self, client, db):
        """Should return 404 when project does not exist."""
        response = client.post(
            "/api/projects/99999/clips/reorder/",
            data=json.dumps({"clip_ids": []}),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_reorder_only_accepts_post(self, client, project_with_clips):
        """Should reject GET requests."""
        response = client.get(f"/api/projects/{project_with_clips.pk}/clips/reorder/")

        assert response.status_code == 405


@pytest.mark.django_db
class TestAddClip:
    """Verify add clip API endpoint."""

    def test_add_clip_creates_at_end(self, client, project_with_clips):
        """Should create a new clip at the next sequence number."""
        project = project_with_clips
        initial_count = project.clips.count()

        response = client.post(
            f"/api/projects/{project.pk}/clips/add/",
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "added"
        assert data["clip"]["sequence_number"] == initial_count + 1
        assert project.clips.count() == initial_count + 1

    def test_add_clip_returns_clip_data(self, client, project_with_clips):
        """Should return complete clip data in the response."""
        response = client.post(
            f"/api/projects/{project_with_clips.pk}/clips/add/",
            content_type="application/json",
        )

        clip_data = response.json()["clip"]
        assert "id" in clip_data
        assert "sequence_number" in clip_data
        assert "script_text" in clip_data
        assert "generation_status" in clip_data
        assert "generation_method" in clip_data
        assert clip_data["script_text"] == ""

    def test_add_clip_rejects_at_max(self, client, project_at_max_clips):
        """Should return 400 when project already has 10 clips."""
        response = client.post(
            f"/api/projects/{project_at_max_clips.pk}/clips/add/",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "Maximum of 10 clips" in response.json()["error"]
        assert project_at_max_clips.clips.count() == 10

    def test_add_clip_returns_404_for_missing_project(self, client, db):
        """Should return 404 when project does not exist."""
        response = client.post(
            "/api/projects/99999/clips/add/",
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_add_clip_only_accepts_post(self, client, project_with_clips):
        """Should reject GET requests."""
        response = client.get(f"/api/projects/{project_with_clips.pk}/clips/add/")

        assert response.status_code == 405

    def test_add_clip_to_empty_project(self, client, db):
        """Should create clip at sequence 1 when project has no clips."""
        project = Project.objects.create(
            title="Empty Project",
            description="No clips yet.",
            num_clips=0,
        )

        response = client.post(
            f"/api/projects/{project.pk}/clips/add/",
            content_type="application/json",
        )

        assert response.status_code == 201
        assert response.json()["clip"]["sequence_number"] == 1


@pytest.mark.django_db
class TestDeleteClip:
    """Verify delete clip API endpoint."""

    def test_delete_clip_removes_it(self, client, project_with_clips):
        """Should delete the clip and return success."""
        project = project_with_clips
        clip_to_delete = project.clips.order_by("sequence_number").last()

        response = client.post(
            f"/api/clips/{clip_to_delete.pk}/delete/",
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        assert project.clips.count() == 2

    def test_delete_clip_resequences_remaining(self, client, project_with_clips):
        """Should resequence remaining clips after deletion."""
        project = project_with_clips
        middle_clip = project.clips.get(sequence_number=2)

        response = client.post(
            f"/api/clips/{middle_clip.pk}/delete/",
            content_type="application/json",
        )

        assert response.status_code == 200
        remaining = list(project.clips.order_by("sequence_number"))
        assert len(remaining) == 2
        assert remaining[0].sequence_number == 1
        assert remaining[1].sequence_number == 2

    def test_delete_rejects_last_clip(self, client, project_with_one_clip):
        """Should return 400 when trying to delete the only clip."""
        clip = project_with_one_clip.clips.first()

        response = client.post(
            f"/api/clips/{clip.pk}/delete/",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "Cannot delete the last clip" in response.json()["error"]
        assert project_with_one_clip.clips.count() == 1

    def test_delete_returns_deleted_sequence(self, client, project_with_clips):
        """Should return the deleted clip's original sequence number."""
        clip = project_with_clips.clips.get(sequence_number=2)

        response = client.post(
            f"/api/clips/{clip.pk}/delete/",
            content_type="application/json",
        )

        assert response.json()["deleted_sequence"] == 2

    def test_delete_returns_404_for_missing_clip(self, client, db):
        """Should return 404 when clip does not exist."""
        response = client.post(
            "/api/clips/99999/delete/",
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_delete_only_accepts_post(self, client, project_with_clips):
        """Should reject GET requests."""
        clip = project_with_clips.clips.first()

        response = client.get(f"/api/clips/{clip.pk}/delete/")

        assert response.status_code == 405

    def test_delete_first_clip_resequences_correctly(self, client, project_with_clips):
        """Should resequence from 1 when first clip is deleted."""
        project = project_with_clips
        first_clip = project.clips.get(sequence_number=1)

        client.post(
            f"/api/clips/{first_clip.pk}/delete/",
            content_type="application/json",
        )

        remaining = list(project.clips.order_by("sequence_number"))
        assert remaining[0].sequence_number == 1
        assert remaining[1].sequence_number == 2
