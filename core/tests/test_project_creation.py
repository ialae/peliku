"""Integration tests for new project creation with AI script generation."""

from unittest.mock import MagicMock, patch

import pytest

from django.test import Client

from core.models import Project
from core.services.ai_client import reset_client


@pytest.fixture(autouse=True)
def _reset_ai_client():
    """Reset the AI client singleton before and after each test."""
    reset_client()
    yield
    reset_client()


@pytest.fixture()
def client():
    """Return a Django test client."""
    return Client()


VALID_FORM_DATA = {
    "title": "Nature Reel",
    "description": "A beautiful reel about forests and rivers in autumn.",
    "visual_style": "Cinematic, warm golden-hour tones",
    "aspect_ratio": "9:16",
    "clip_duration": "8",
    "num_clips": "5",
}


def _mock_ai_scripts(count):
    """Return a list of mock script strings for the given clip count."""
    return [f"AI-generated script for clip {i}" for i in range(1, count + 1)]


def _make_mock_response(text):
    """Create a mock Gemini API response."""
    mock_response = MagicMock()
    mock_response.text = text
    return mock_response


@pytest.mark.django_db
class TestProjectCreationSuccess:
    """Test successful project creation with AI scripts."""

    @patch("core.views.generate_all_scripts")
    def test_creates_project_and_clips(self, mock_generate, client):
        """Form submission creates a project and clips with AI scripts."""
        scripts = _mock_ai_scripts(5)
        mock_generate.return_value = scripts

        client.post("/projects/new/", VALID_FORM_DATA)

        assert Project.objects.count() == 1
        project = Project.objects.first()
        assert project.title == "Nature Reel"
        assert project.description == VALID_FORM_DATA["description"]
        assert project.num_clips == 5
        assert project.clips.count() == 5

    @patch("core.views.generate_all_scripts")
    def test_clips_have_ai_scripts(self, mock_generate, client):
        """Each clip receives the AI-generated script text."""
        scripts = _mock_ai_scripts(5)
        mock_generate.return_value = scripts

        client.post("/projects/new/", VALID_FORM_DATA)

        project = Project.objects.first()
        clips = list(project.clips.order_by("sequence_number"))
        for i, clip in enumerate(clips):
            assert clip.script_text == scripts[i]
            assert clip.sequence_number == i + 1

    @patch("core.views.generate_all_scripts")
    def test_redirects_to_workspace(self, mock_generate, client):
        """After creation, the user is redirected to the workspace."""
        mock_generate.return_value = _mock_ai_scripts(5)

        response = client.post("/projects/new/", VALID_FORM_DATA)

        project = Project.objects.first()
        assert response.status_code == 302
        assert response.url == f"/projects/{project.pk}/"

    @patch("core.views.generate_all_scripts")
    def test_calls_generate_all_scripts(self, mock_generate, client):
        """The AI generation service is called with the new project."""
        mock_generate.return_value = _mock_ai_scripts(5)

        client.post("/projects/new/", VALID_FORM_DATA)

        mock_generate.assert_called_once()
        project_arg = mock_generate.call_args[0][0]
        assert project_arg.title == "Nature Reel"

    @patch("core.views.generate_all_scripts")
    def test_visual_style_optional(self, mock_generate, client):
        """Project can be created without visual style."""
        mock_generate.return_value = _mock_ai_scripts(5)
        data = {**VALID_FORM_DATA, "visual_style": ""}

        response = client.post("/projects/new/", data)

        assert response.status_code == 302
        project = Project.objects.first()
        assert project.visual_style == ""


@pytest.mark.django_db
class TestProjectCreationValidation:
    """Test form validation for project creation."""

    def test_missing_title_shows_error(self, client):
        """Submitting without a title returns the form with an error."""
        data = {**VALID_FORM_DATA, "title": ""}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0
        assert b"Title is required" in response.content

    def test_missing_description_shows_error(self, client):
        """Submitting without a description returns the form with an error."""
        data = {**VALID_FORM_DATA, "description": ""}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0
        assert b"Description is required" in response.content

    def test_title_too_long_shows_error(self, client):
        """Title exceeding 100 characters returns an error."""
        data = {**VALID_FORM_DATA, "title": "x" * 101}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0

    def test_invalid_aspect_ratio_shows_error(self, client):
        """Invalid aspect ratio returns an error."""
        data = {**VALID_FORM_DATA, "aspect_ratio": "4:3"}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0

    def test_invalid_clip_duration_shows_error(self, client):
        """Invalid clip duration returns an error."""
        data = {**VALID_FORM_DATA, "clip_duration": "10"}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0

    def test_invalid_num_clips_shows_error(self, client):
        """Number of clips outside 5-10 returns an error."""
        data = {**VALID_FORM_DATA, "num_clips": "15"}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        assert Project.objects.count() == 0

    def test_preserves_form_data_on_error(self, client):
        """Failed validation re-renders the form with submitted values."""
        data = {**VALID_FORM_DATA, "title": ""}

        response = client.post("/projects/new/", data)

        assert response.status_code == 200
        content = response.content.decode()
        assert VALID_FORM_DATA["description"] in content


@pytest.mark.django_db
class TestProjectCreationAIFailure:
    """Test graceful fallback when AI generation fails."""

    @patch("core.views.generate_all_scripts")
    def test_creates_empty_clips_on_ai_error(self, mock_generate, client):
        """If AI fails, clips are created with empty scripts."""
        mock_generate.side_effect = RuntimeError("API unavailable")

        response = client.post("/projects/new/", VALID_FORM_DATA)

        assert response.status_code == 302
        project = Project.objects.first()
        assert project is not None
        assert project.clips.count() == 5
        for clip in project.clips.all():
            assert clip.script_text == ""

    @patch("core.views.generate_all_scripts")
    def test_redirects_despite_ai_error(self, mock_generate, client):
        """User still reaches the workspace even if AI fails."""
        mock_generate.side_effect = ValueError("Parse error")

        response = client.post("/projects/new/", VALID_FORM_DATA)

        project = Project.objects.first()
        assert response.status_code == 302
        assert response.url == f"/projects/{project.pk}/"
