"""Tests for Sprint 7: Settings panel, preview overlay, and responsive layout."""

import pytest

from django.test import Client

from core.models import Clip, Project


@pytest.mark.django_db
class TestSettingsPanel:
    """Verify the settings slide-over panel markup is rendered."""

    def setup_method(self):
        """Set up a test client for each test."""
        self.client = Client()

    def test_home_page_contains_settings_panel(self):
        """Should render the settings panel partial on the home page."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-settings-panel" in content

    def test_settings_panel_has_close_button(self):
        """Should render a close button in the settings panel."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-settings-close" in content

    def test_settings_panel_contains_aspect_ratio_field(self):
        """Should render the default aspect ratio toggle in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'name="default_aspect_ratio"' in content

    def test_settings_panel_contains_clip_duration_field(self):
        """Should render the default clip duration select in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "settings-clip-duration" in content

    def test_settings_panel_contains_num_clips_field(self):
        """Should render the default number of clips select in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "settings-num-clips" in content

    def test_settings_panel_contains_visual_style_field(self):
        """Should render the default visual style textarea in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "settings-visual-style" in content

    def test_settings_panel_contains_video_quality_field(self):
        """Should render the video quality select in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "settings-video-quality" in content

    def test_settings_panel_contains_generation_speed_field(self):
        """Should render the generation speed toggle in settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'name="generation_speed"' in content

    def test_settings_panel_has_backdrop(self):
        """Should render the settings backdrop element."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-settings-backdrop" in content

    def test_settings_panel_on_workspace_page(self):
        """Should render settings panel on the workspace page too."""
        project = Project.objects.create(
            title="Test",
            description="d",
            num_clips=1,
        )
        Clip.objects.create(project=project, sequence_number=1)
        response = self.client.get(f"/projects/{project.pk}/")
        content = response.content.decode()
        assert "js-settings-panel" in content


@pytest.mark.django_db
class TestPreviewOverlay:
    """Verify the preview overlay markup is rendered on the workspace."""

    def setup_method(self):
        """Set up a test client and create a project for workspace tests."""
        self.client = Client()
        self.project = Project.objects.create(
            title="Preview Test",
            description="d",
            num_clips=2,
        )
        for seq in range(1, 3):
            Clip.objects.create(project=self.project, sequence_number=seq)
        self.workspace_url = f"/projects/{self.project.pk}/"

    def test_workspace_contains_preview_overlay(self):
        """Should render the preview overlay on the workspace page."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "js-preview-overlay" in content

    def test_preview_overlay_has_close_button(self):
        """Should render a close button in the preview overlay."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "js-preview-close-btn" in content

    def test_preview_overlay_has_scrubber(self):
        """Should render the timeline scrubber in the preview overlay."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "preview-overlay__scrubber" in content

    def test_preview_overlay_has_playback_controls(self):
        """Should render playback controls in the preview overlay."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "preview-overlay__controls" in content

    def test_preview_overlay_has_video_placeholder(self):
        """Should render a video placeholder in the preview overlay."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "preview-overlay__video-placeholder" in content

    def test_preview_overlay_not_on_home_page(self):
        """Should NOT render the preview overlay on the home page."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-preview-overlay" not in content

    def test_preview_toggle_button_exists(self):
        """Should render the Preview Reel button with the js toggle class."""
        response = self.client.get(self.workspace_url)
        content = response.content.decode()
        assert "js-preview-toggle" in content


@pytest.mark.django_db
class TestResponsiveSetup:
    """Verify responsive CSS is loaded and viewport meta tag is present."""

    def setup_method(self):
        """Set up a test client for each test."""
        self.client = Client()

    def test_responsive_css_is_loaded(self):
        """Should include responsive.css in the page."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "responsive.css" in content

    def test_viewport_meta_tag_is_present(self):
        """Should include a viewport meta tag for responsive design."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'name="viewport"' in content
        assert "width=device-width" in content
