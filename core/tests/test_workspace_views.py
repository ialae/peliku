"""Tests for workspace view (clip rendering) and script update API endpoint."""

import json

import pytest

from django.test import Client

from core.models import Clip, Project


@pytest.mark.django_db
class TestWorkspaceClipDisplay:
    """Verify workspace renders real clip scripts from the database."""

    def setup_method(self):
        """Create a project with clips containing script text."""
        self.client = Client()
        self.project = Project.objects.create(
            title="Script Display Project",
            description="Testing clip script display",
            aspect_ratio="9:16",
            clip_duration=8,
            num_clips=3,
        )
        self.scripts = [
            "Opening shot: a sunrise over the ocean, warm tones.",
            "Middle scene: character walks along the beach.",
            "Final clip: wide aerial shot pulling away.",
        ]
        for seq, script in enumerate(self.scripts, start=1):
            Clip.objects.create(
                project=self.project,
                sequence_number=seq,
                script_text=script,
            )
        self.url = f"/projects/{self.project.pk}/"

    def test_workspace_displays_clip_scripts(self):
        """Should render each clip's script text in the page."""
        response = self.client.get(self.url)
        content = response.content.decode()
        for script in self.scripts:
            assert script in content

    def test_workspace_displays_clip_numbers(self):
        """Should display 'Clip 1', 'Clip 2', 'Clip 3' headings."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Clip 1" in content
        assert "Clip 2" in content
        assert "Clip 3" in content

    def test_workspace_clips_ordered_by_sequence(self):
        """Should render clips in sequence_number order."""
        response = self.client.get(self.url)
        content = response.content.decode()
        pos_clip1 = content.index("Clip 1")
        pos_clip2 = content.index("Clip 2")
        pos_clip3 = content.index("Clip 3")
        assert pos_clip1 < pos_clip2 < pos_clip3

    def test_workspace_shows_character_count(self):
        """Should show character count for the first clip's script."""
        response = self.client.get(self.url)
        content = response.content.decode()
        expected_len = str(len(self.scripts[0]))
        assert expected_len in content

    def test_workspace_textarea_has_clip_id(self):
        """Should include data-clip-id attribute on each clip card."""
        response = self.client.get(self.url)
        content = response.content.decode()
        for clip in self.project.clips.all():
            assert f'data-clip-id="{clip.pk}"' in content

    def test_workspace_project_title_in_header(self):
        """Should show the project title in the workspace header."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Script Display Project" in content

    def test_workspace_description_in_header(self):
        """Should show the project description in the workspace header."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Testing clip script display" in content

    def test_workspace_contains_csrf_token(self):
        """Should include a CSRF token for AJAX requests."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content


@pytest.mark.django_db
class TestUpdateClipScriptAPI:
    """Verify the POST /api/clips/<id>/update-script/ endpoint."""

    def setup_method(self):
        """Create a project with a clip for testing the update API."""
        self.client = Client()
        self.project = Project.objects.create(
            title="API Test Project",
            description="Testing script update API",
            aspect_ratio="9:16",
            clip_duration=8,
            num_clips=1,
        )
        self.clip = Clip.objects.create(
            project=self.project,
            sequence_number=1,
            script_text="Original script text.",
        )
        self.url = f"/api/clips/{self.clip.pk}/update-script/"

    def test_update_script_returns_200(self):
        """Should return 200 on a valid update."""
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": "Updated script."}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_update_script_saves_text(self):
        """Should persist the new script_text to the database."""
        self.client.post(
            self.url,
            data=json.dumps({"script_text": "Brand new script content."}),
            content_type="application/json",
        )
        self.clip.refresh_from_db()
        assert self.clip.script_text == "Brand new script content."

    def test_update_script_returns_json(self):
        """Should return JSON with status and clip_id."""
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": "Test."}),
            content_type="application/json",
        )
        data = response.json()
        assert data["status"] == "updated"
        assert data["clip_id"] == self.clip.pk

    def test_update_script_empty_string_allowed(self):
        """Should allow saving an empty script."""
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": ""}),
            content_type="application/json",
        )
        assert response.status_code == 200
        self.clip.refresh_from_db()
        assert self.clip.script_text == ""

    def test_update_script_invalid_json(self):
        """Should return 400 for invalid JSON body."""
        response = self.client.post(
            self.url,
            data="not json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_update_script_missing_field(self):
        """Should return 400 when script_text is missing."""
        response = self.client.post(
            self.url,
            data=json.dumps({"other_field": "value"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_update_script_too_long(self):
        """Should return 400 when script exceeds 2000 characters."""
        long_text = "x" * 2001
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": long_text}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_update_script_max_length_allowed(self):
        """Should allow exactly 2000 characters."""
        max_text = "y" * 2000
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": max_text}),
            content_type="application/json",
        )
        assert response.status_code == 200
        self.clip.refresh_from_db()
        assert self.clip.script_text == max_text

    def test_update_script_nonexistent_clip(self):
        """Should return 404 for a nonexistent clip ID."""
        response = self.client.post(
            "/api/clips/99999/update-script/",
            data=json.dumps({"script_text": "Test."}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_update_script_get_not_allowed(self):
        """Should return 405 for a GET request."""
        response = self.client.get(self.url)
        assert response.status_code == 405

    def test_update_script_non_string_rejected(self):
        """Should return 400 when script_text is not a string."""
        response = self.client.post(
            self.url,
            data=json.dumps({"script_text": 12345}),
            content_type="application/json",
        )
        assert response.status_code == 400
