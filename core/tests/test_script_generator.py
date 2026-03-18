"""Tests for the AI script generation service."""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.models import Clip, Project
from core.services.ai_client import reset_client
from core.services.script_generator import (
    _parse_script_list,
    generate_all_scripts,
    regenerate_all_scripts,
    regenerate_single_script,
)


@pytest.fixture(autouse=True)
def _reset_ai_client():
    """Reset the AI client singleton before each test."""
    reset_client()
    yield
    reset_client()


@pytest.fixture()
def project(db):
    """Create a test project with clips."""
    proj = Project.objects.create(
        title="Test Reel",
        description="A test reel about nature and wildlife",
        visual_style="Cinematic, warm tones",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=5,
    )
    for i in range(1, 6):
        Clip.objects.create(
            project=proj,
            sequence_number=i,
            script_text=f"Script for clip {i}",
        )
    return proj


def _make_mock_response(text):
    """Create a mock Gemini API response with the given text."""
    mock_response = MagicMock()
    mock_response.text = text
    return mock_response


class TestParseScriptList:
    """Tests for the _parse_script_list helper."""

    def test_parses_valid_json_array(self):
        scripts = ["Script one", "Script two", "Script three"]
        result = _parse_script_list(json.dumps(scripts), 3)
        assert result == scripts

    def test_strips_markdown_code_fence(self):
        scripts = ["Script A", "Script B"]
        raw = f"```json\n{json.dumps(scripts)}\n```"
        result = _parse_script_list(raw, 2)
        assert result == scripts

    def test_raises_on_wrong_count(self):
        scripts = ["Only one"]
        with pytest.raises(ValueError, match="Expected 3 scripts, got 1"):
            _parse_script_list(json.dumps(scripts), 3)

    def test_raises_on_non_array(self):
        with pytest.raises(ValueError, match="Expected a JSON array"):
            _parse_script_list('{"key": "value"}', 1)

    def test_raises_on_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_script_list("not json at all", 1)

    def test_converts_non_string_items(self):
        result = _parse_script_list("[1, 2, 3]", 3)
        assert result == ["1", "2", "3"]


@pytest.mark.django_db
class TestGenerateAllScripts:
    """Tests for generate_all_scripts."""

    @patch("core.services.script_generator.get_ai_client")
    def test_returns_correct_number_of_scripts(self, mock_get_client, project):
        scripts = [f"Generated script {i}" for i in range(1, 6)]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            json.dumps(scripts)
        )
        mock_get_client.return_value = mock_client

        result = generate_all_scripts(project)

        assert len(result) == 5
        assert result == scripts

    @patch("core.services.script_generator.get_ai_client")
    def test_passes_project_details_in_prompt(self, mock_get_client, project):
        scripts = [f"Script {i}" for i in range(1, 6)]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            json.dumps(scripts)
        )
        mock_get_client.return_value = mock_client

        generate_all_scripts(project)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "Test Reel" in prompt
        assert "nature and wildlife" in prompt
        assert "9:16" in prompt
        assert "8 seconds" in prompt
        assert "Cinematic, warm tones" in prompt

    @patch("core.services.script_generator.get_ai_client")
    def test_uses_system_instruction(self, mock_get_client, project):
        scripts = [f"Script {i}" for i in range(1, 6)]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            json.dumps(scripts)
        )
        mock_get_client.return_value = mock_client

        generate_all_scripts(project)

        call_args = mock_client.models.generate_content.call_args
        config = call_args.kwargs["config"]
        assert "scriptwriter" in config.system_instruction.lower()

    @patch("core.services.script_generator.get_ai_client")
    def test_raises_on_api_error(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError(
            "API unavailable"
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(RuntimeError, match="API unavailable"):
            generate_all_scripts(project)

    @patch("core.services.script_generator.get_ai_client")
    def test_raises_on_malformed_response(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            "not valid json"
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(json.JSONDecodeError):
            generate_all_scripts(project)


@pytest.mark.django_db
class TestRegenerateSingleScript:
    """Tests for regenerate_single_script."""

    @patch("core.services.script_generator.get_ai_client")
    def test_returns_new_script_text(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            "Brand new script for clip 3"
        )
        mock_get_client.return_value = mock_client

        clip = project.clips.get(sequence_number=3)
        result = regenerate_single_script(clip)

        assert result == "Brand new script for clip 3"

    @patch("core.services.script_generator.get_ai_client")
    def test_includes_neighbor_context(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            "Regenerated clip 3"
        )
        mock_get_client.return_value = mock_client

        clip = project.clips.get(sequence_number=3)
        regenerate_single_script(clip)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "Script for clip 2" in prompt
        assert "Script for clip 4" in prompt

    @patch("core.services.script_generator.get_ai_client")
    def test_first_clip_has_no_previous_context(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            "New first clip"
        )
        mock_get_client.return_value = mock_client

        clip = project.clips.get(sequence_number=1)
        regenerate_single_script(clip)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "Previous clip script" not in prompt
        assert "Next clip script" in prompt

    @patch("core.services.script_generator.get_ai_client")
    def test_last_clip_has_no_next_context(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            "New last clip"
        )
        mock_get_client.return_value = mock_client

        clip = project.clips.get(sequence_number=5)
        regenerate_single_script(clip)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "Previous clip script" in prompt
        assert "Next clip script" not in prompt

    @patch("core.services.script_generator.get_ai_client")
    def test_raises_on_api_error(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError(
            "Connection refused"
        )
        mock_get_client.return_value = mock_client

        clip = project.clips.get(sequence_number=2)
        with pytest.raises(RuntimeError, match="Connection refused"):
            regenerate_single_script(clip)


@pytest.mark.django_db
class TestRegenerateAllScripts:
    """Tests for regenerate_all_scripts."""

    @patch("core.services.script_generator.get_ai_client")
    def test_returns_correct_number_of_scripts(self, mock_get_client, project):
        scripts = [f"New script {i}" for i in range(1, 6)]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            json.dumps(scripts)
        )
        mock_get_client.return_value = mock_client

        result = regenerate_all_scripts(project)

        assert len(result) == 5
        assert result == scripts

    @patch("core.services.script_generator.get_ai_client")
    def test_uses_current_clip_count(self, mock_get_client, project):
        """Uses actual clip count, not project.num_clips."""
        Clip.objects.create(
            project=project,
            sequence_number=6,
            script_text="Extra clip",
        )
        scripts = [f"Script {i}" for i in range(1, 7)]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response(
            json.dumps(scripts)
        )
        mock_get_client.return_value = mock_client

        result = regenerate_all_scripts(project)

        assert len(result) == 6

    @patch("core.services.script_generator.get_ai_client")
    def test_raises_on_api_error(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("Quota exceeded")
        mock_get_client.return_value = mock_client

        with pytest.raises(RuntimeError, match="Quota exceeded"):
            regenerate_all_scripts(project)

    @patch("core.services.script_generator.get_ai_client")
    def test_raises_on_malformed_response(self, mock_get_client, project):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_mock_response("[]")
        mock_get_client.return_value = mock_client

        with pytest.raises(ValueError, match="Expected 5 scripts, got 0"):
            regenerate_all_scripts(project)
