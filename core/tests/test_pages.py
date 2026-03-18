"""Tests for the Home page and New Project form page shells."""

import pytest

from django.test import Client

from core.models import Project


@pytest.mark.django_db
class TestHomePage:
    """Verify home page renders with expected empty-state elements."""

    def setup_method(self):
        """Set up a test client for each test."""
        self.client = Client()

    def test_home_page_returns_200(self):
        """Should return 200 when visiting the home page."""
        response = self.client.get("/")
        assert response.status_code == 200

    def test_home_page_contains_new_project_button(self):
        """Should contain a 'New Project' link/button."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "New Project" in content

    def test_home_page_contains_empty_state_heading(self):
        """Should show appropriate empty state heading when no projects exist."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "No projects yet" in content

    def test_home_page_contains_empty_state_cta(self):
        """Should show a call-to-action message in the empty state."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "Forge your first reel to get started" in content

    def test_home_page_header_has_new_project_link(self):
        """Should have a New Project button in the header linking to /projects/new/."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "/projects/new/" in content

    def test_home_page_contains_search_bar(self):
        """Should contain a search bar when projects exist."""
        Project.objects.create(title="Test", description="d")
        response = self.client.get("/")
        content = response.content.decode()
        assert "Search projects" in content

    def test_home_page_contains_project_grid_area(self):
        """Should contain a project grid area div when projects exist."""
        Project.objects.create(title="Test", description="d")
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-project-grid" in content


@pytest.mark.django_db
class TestProjectFormPage:
    """Verify new project form page renders with all expected fields."""

    def setup_method(self):
        """Set up a test client for each test."""
        self.client = Client()

    def test_form_page_returns_200(self):
        """Should return 200 when visiting the new project form."""
        response = self.client.get("/projects/new/")
        assert response.status_code == 200

    def test_form_page_contains_generate_scripts_button(self):
        """Should contain the 'Generate Scripts' submit button."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert "Generate Scripts" in content

    def test_form_page_contains_title_field(self):
        """Should contain a title input field."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="title"' in content

    def test_form_page_contains_description_field(self):
        """Should contain a description textarea."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="description"' in content

    def test_form_page_contains_aspect_ratio_toggle(self):
        """Should contain aspect ratio radio inputs."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="aspect_ratio"' in content
        assert "9:16" in content
        assert "16:9" in content

    def test_form_page_contains_clip_duration_select(self):
        """Should contain a clip duration select."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="clip_duration"' in content

    def test_form_page_contains_visual_style_field(self):
        """Should contain a visual style textarea."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="visual_style"' in content

    def test_form_page_contains_num_clips_select(self):
        """Should contain a number of clips select."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert 'name="num_clips"' in content

    def test_form_page_contains_char_count_indicators(self):
        """Should contain character count elements for description and visual style."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert "js-char-count" in content
        assert "2000" in content
        assert "500" in content

    def test_form_page_contains_csrf_token(self):
        """Should contain a CSRF token for form security."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content

    def test_form_page_back_navigation_via_logo(self):
        """Should contain Peliku logo link back to home page."""
        response = self.client.get("/projects/new/")
        content = response.content.decode()
        assert "Peliku" in content
