"""Tests for the Project Workspace page shell."""

import pytest

from django.test import Client

from core.models import Clip, Project


@pytest.mark.django_db
class TestWorkspacePage:
    """Verify workspace page renders with clip panels and expected elements."""

    def setup_method(self):
        """Set up a test client and create a real project with clips."""
        self.client = Client()
        self.project = Project.objects.create(
            title="Untitled Project",
            description="A test project",
            visual_style="Cinematic, warm golden-hour tones",
            aspect_ratio="9:16",
            clip_duration=8,
            num_clips=3,
        )
        for seq in range(1, 4):
            Clip.objects.create(
                project=self.project,
                sequence_number=seq,
                script_text=f"Script for clip {seq}",
            )
        self.url = f"/projects/{self.project.pk}/"

    def test_workspace_returns_200(self):
        """Should return 200 for a valid project."""
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_workspace_contains_project_title(self):
        """Should show the project title."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Untitled Project" in content

    def test_workspace_contains_aspect_ratio_badge(self):
        """Should display the aspect ratio badge."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "9:16" in content

    def test_workspace_contains_clip_duration_badge(self):
        """Should display the clip duration badge."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "8s clips" in content

    def test_workspace_contains_generate_video_button(self):
        """Should have a 'Generate Video' button for each clip."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Generate Video" in content

    def test_workspace_contains_regenerate_script_button(self):
        """Should have a 'Regenerate Script' button for each clip."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Regenerate Script" in content

    def test_workspace_contains_three_clip_cards(self):
        """Should render three clip cards."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Clip 1" in content
        assert "Clip 2" in content
        assert "Clip 3" in content

    def test_workspace_contains_script_textareas(self):
        """Should render a script textarea per clip."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert 'id="script-1"' in content
        assert 'id="script-2"' in content
        assert 'id="script-3"' in content

    def test_workspace_contains_reference_panel(self):
        """Should render the Reference Images Panel."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Reference Images" in content

    def test_workspace_reference_panel_has_three_slots(self):
        """Should render 3 reference image slots."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Slot 1" in content
        assert "Slot 2" in content
        assert "Slot 3" in content

    def test_workspace_contains_connector_lines(self):
        """Should render transition frame buttons between clips."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Generate Transition Frame" in content

    def test_workspace_contains_generation_method_dropdown(self):
        """Should have a generation method dropdown per clip."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Text-to-Video" in content
        assert "Image-to-Video" in content
        assert "Frame Interpolation" in content

    def test_workspace_contains_header_actions(self):
        """Should show disabled header action buttons."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Regenerate All Scripts" in content
        assert "Preview Reel" in content
        assert "Download Reel" in content

    def test_workspace_contains_visual_style(self):
        """Should display the visual style when present."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Cinematic, warm golden-hour tones" in content

    def test_workspace_loads_workspace_css(self):
        """Should include workspace.css link."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "workspace.css" in content

    def test_workspace_loads_workspace_js(self):
        """Should include workspace.js script tag."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "workspace.js" in content

    def test_workspace_nonexistent_project_returns_404(self):
        """Should return 404 for a nonexistent project."""
        response = self.client.get("/projects/99999/")
        assert response.status_code == 404

    def test_workspace_contains_drag_handles(self):
        """Should render drag handles on clip cards."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "ph-dots-six-vertical" in content

    def test_workspace_ref_panel_collapsed_by_default(self):
        """Should have the reference panel collapsed (aria-expanded=false)."""
        response = self.client.get(self.url)
        content = response.content.decode()
        assert 'aria-expanded="false"' in content
