"""Tests for transition frame generation API and service."""

from unittest.mock import MagicMock, patch

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
    """Create a test project with 3 clips."""
    proj = Project.objects.create(
        title="Transition Test Reel",
        description="A reel for testing transition frame generation",
        visual_style="Cinematic, dark tones",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=3,
    )
    for i in range(1, 4):
        Clip.objects.create(
            project=proj,
            sequence_number=i,
            script_text=f"Script for clip {i} with some action.",
        )
    return proj


@pytest.fixture()
def api_client():
    """Return a Django test client."""
    return Client()


@pytest.mark.django_db
class TestGenerateTransitionEndpoint:
    """Tests for POST /api/clips/<id>/generate-transition/."""

    def test_returns_202_with_task_id(self, api_client, project):
        """Should return 202 with a task_id for a valid upper clip."""
        clip_above = project.clips.get(sequence_number=1)
        with patch("core.services.transition_generator.generate_transition_frames"):
            response = api_client.post(
                f"/api/clips/{clip_above.pk}/generate-transition/",
                content_type="application/json",
            )

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert isinstance(data["task_id"], int)

    def test_returns_400_when_no_next_clip(self, api_client, project):
        """Should return 400 when the upper clip is the last clip."""
        last_clip = project.clips.get(sequence_number=3)
        response = api_client.post(
            f"/api/clips/{last_clip.pk}/generate-transition/",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "No next clip" in response.json()["error"]

    def test_returns_404_for_missing_clip(self, api_client, db):
        """Should return 404 for a non-existent clip ID."""
        response = api_client.post(
            "/api/clips/99999/generate-transition/",
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_rejects_get_request(self, api_client, project):
        """Should reject GET requests with 405."""
        clip = project.clips.get(sequence_number=1)
        response = api_client.get(
            f"/api/clips/{clip.pk}/generate-transition/",
        )

        assert response.status_code == 405

    def test_works_for_middle_clip(self, api_client, project):
        """Should accept a middle clip (clip 2) as the upper clip."""
        clip_above = project.clips.get(sequence_number=2)
        with patch("core.services.transition_generator.generate_transition_frames"):
            response = api_client.post(
                f"/api/clips/{clip_above.pk}/generate-transition/",
                content_type="application/json",
            )

        assert response.status_code == 202


@pytest.mark.django_db
class TestGenerateTransitionFramesService:
    """Tests for the generate_transition_frames service function."""

    @patch("core.services.transition_generator._generate_image")
    def test_generates_both_frames_and_saves(self, mock_gen, project):
        """Should generate two images and set clip fields."""
        mock_gen.return_value = b"fake-png-data"

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        result = generate_transition_frames(clip_above, clip_below)

        assert mock_gen.call_count == 2
        assert "last_frame_path" in result
        assert "first_frame_path" in result

        clip_above.refresh_from_db()
        clip_below.refresh_from_db()
        assert clip_above.last_frame.name == result["last_frame_path"]
        assert clip_below.first_frame.name == result["first_frame_path"]

    @patch("core.services.transition_generator._generate_image")
    def test_uses_correct_prompts(self, mock_gen, project):
        """Should pass both clip scripts into the prompts."""
        mock_gen.return_value = b"fake-png-data"

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        generate_transition_frames(clip_above, clip_below)

        ending_prompt = mock_gen.call_args_list[0][0][0]
        starting_prompt = mock_gen.call_args_list[1][0][0]

        assert clip_above.script_text in ending_prompt
        assert clip_below.script_text in ending_prompt
        assert clip_above.script_text in starting_prompt
        assert clip_below.script_text in starting_prompt

    @patch("core.services.transition_generator._generate_image")
    def test_saves_files_to_disk(self, mock_gen, project, tmp_path, settings):
        """Should write image bytes to the media frames directory."""
        settings.MEDIA_ROOT = str(tmp_path)
        mock_gen.return_value = b"fake-png-bytes-here"

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        result = generate_transition_frames(clip_above, clip_below)

        last_path = tmp_path / result["last_frame_path"]
        first_path = tmp_path / result["first_frame_path"]
        assert last_path.exists()
        assert first_path.exists()
        assert last_path.read_bytes() == b"fake-png-bytes-here"
        assert first_path.read_bytes() == b"fake-png-bytes-here"

    @patch("core.services.transition_generator._generate_image")
    def test_does_not_affect_other_clips(self, mock_gen, project):
        """Should not modify clip 3 when generating between 1 and 2."""
        mock_gen.return_value = b"fake-png-data"

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)
        clip_three = project.clips.get(sequence_number=3)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        generate_transition_frames(clip_above, clip_below)

        clip_three.refresh_from_db()
        assert not clip_three.first_frame.name
        assert not clip_three.last_frame.name

    @patch("core.services.transition_generator._generate_image")
    def test_raises_on_image_generation_failure(self, mock_gen, project):
        """Should propagate RuntimeError when image generation fails."""
        mock_gen.side_effect = RuntimeError("API error")

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        with pytest.raises(RuntimeError, match="API error"):
            generate_transition_frames(clip_above, clip_below)

    @patch("core.services.transition_generator._generate_image")
    def test_returns_relative_paths(self, mock_gen, project):
        """Should return paths relative to MEDIA_ROOT."""
        mock_gen.return_value = b"fake-png-data"

        clip_above = project.clips.get(sequence_number=1)
        clip_below = project.clips.get(sequence_number=2)

        from core.services.transition_generator import (
            generate_transition_frames,
        )

        result = generate_transition_frames(clip_above, clip_below)

        assert result["last_frame_path"].startswith("images/frames/")
        assert result["first_frame_path"].startswith("images/frames/")
        assert result["last_frame_path"].endswith(".png")
        assert result["first_frame_path"].endswith(".png")


@pytest.mark.django_db
class TestGenerateTransitionImageHelper:
    """Tests for the _generate_image internal helper."""

    def test_calls_gemini_api_correctly(self):
        """Should call the Gemini client with correct model and config."""
        mock_client = MagicMock()

        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"generated-image-bytes"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_client.models.generate_content.return_value = MagicMock(
            candidates=[mock_candidate]
        )

        with patch(
            "core.services.transition_generator.get_ai_client",
            return_value=mock_client,
        ):
            from core.services.transition_generator import _generate_image

            result = _generate_image("test prompt")

        assert result == b"generated-image-bytes"
        mock_client.models.generate_content.assert_called_once()

    def test_raises_when_no_candidates(self):
        """Should raise RuntimeError when API returns no candidates."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MagicMock(candidates=[])

        with patch(
            "core.services.transition_generator.get_ai_client",
            return_value=mock_client,
        ):
            from core.services.transition_generator import _generate_image

            with pytest.raises(RuntimeError, match="no candidates"):
                _generate_image("test prompt")

    def test_raises_when_no_image_data(self):
        """Should raise RuntimeError when response has no image parts."""
        mock_client = MagicMock()

        mock_part = MagicMock(spec=[])
        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_client.models.generate_content.return_value = MagicMock(
            candidates=[mock_candidate]
        )

        with patch(
            "core.services.transition_generator.get_ai_client",
            return_value=mock_client,
        ):
            from core.services.transition_generator import _generate_image

            with pytest.raises(RuntimeError, match="no image data"):
                _generate_image("test prompt")
