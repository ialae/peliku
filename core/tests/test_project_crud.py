"""Tests for Home page CRUD: list, create, delete, rename, duplicate, search."""

import json

import pytest

from django.test import Client

from core.models import Clip, Project, ReferenceImage, UserSettings


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def sample_project(db):
    """Create and return a sample project with clips."""
    project = Project.objects.create(
        title="Test Project",
        description="A test project for unit tests.",
        visual_style="Cinematic tones",
        aspect_ratio="9:16",
        clip_duration=8,
        num_clips=5,
    )
    for seq in range(1, 6):
        Clip.objects.create(
            project=project,
            sequence_number=seq,
            script_text=f"Script for clip {seq}",
        )
    return project


@pytest.fixture
def sample_project_with_ref(sample_project):
    """Create a project with a reference image."""
    ReferenceImage.objects.create(
        project=sample_project,
        slot_number=1,
        image_file="images/references/placeholder.png",
        label="Test reference",
    )
    return sample_project


@pytest.fixture
def multiple_projects(db):
    """Create multiple projects for list and search tests."""
    projects = []
    for title in ["Alpha Reel", "Beta Reel", "Gamma Reel"]:
        project = Project.objects.create(
            title=title,
            description=f"Description for {title}",
            num_clips=5,
        )
        for seq in range(1, 6):
            Clip.objects.create(
                project=project,
                sequence_number=seq,
                script_text=f"Clip {seq} script",
            )
        projects.append(project)
    return projects


@pytest.mark.django_db
class TestListProjects:
    """Verify home page lists projects from the database."""

    def test_home_shows_empty_state_when_no_projects(self, client):
        """Should show the empty state when database has no projects."""
        response = client.get("/")
        content = response.content.decode()
        assert "No projects yet" in content

    def test_home_shows_project_cards_when_projects_exist(self, client, sample_project):
        """Should render project cards with title and clip progress."""
        response = client.get("/")
        content = response.content.decode()
        assert sample_project.title in content
        assert "0/5 clips generated" in content

    def test_home_shows_multiple_projects(self, client, multiple_projects):
        """Should render all existing projects as cards."""
        response = client.get("/")
        content = response.content.decode()
        for project in multiple_projects:
            assert project.title in content

    def test_home_shows_aspect_ratio_badge(self, client, sample_project):
        """Should display the aspect ratio badge on each card."""
        response = client.get("/")
        content = response.content.decode()
        assert "9:16" in content

    def test_home_hides_empty_state_when_projects_exist(self, client, sample_project):
        """Should not display empty state when projects are present."""
        response = client.get("/")
        content = response.content.decode()
        assert "No projects yet" not in content

    def test_home_shows_search_bar_when_projects_exist(self, client, sample_project):
        """Should display an active search bar when projects exist."""
        response = client.get("/")
        content = response.content.decode()
        assert "js-search-input" in content

    def test_home_project_links_to_workspace(self, client, sample_project):
        """Should link each project card to its workspace."""
        response = client.get("/")
        content = response.content.decode()
        expected_url = f"/projects/{sample_project.pk}/"
        assert expected_url in content


@pytest.mark.django_db
class TestCreateProject:
    """Verify project creation via the new-project form POST."""

    def test_create_project_redirects_to_workspace(self, client):
        """Should create a project and redirect to its workspace."""
        response = client.post(
            "/projects/new/",
            {
                "title": "New Reel",
                "description": "A cool reel about cats.",
                "aspect_ratio": "9:16",
                "clip_duration": "8",
                "num_clips": "7",
            },
        )
        project = Project.objects.get(title="New Reel")
        assert response.status_code == 302
        assert f"/projects/{project.pk}/" in response.url

    def test_create_project_creates_clips(self, client):
        """Should create the correct number of empty clips."""
        client.post(
            "/projects/new/",
            {
                "title": "Clipped Reel",
                "description": "Testing clips.",
                "aspect_ratio": "16:9",
                "clip_duration": "6",
                "num_clips": "5",
            },
        )
        project = Project.objects.get(title="Clipped Reel")
        assert project.clips.count() == 5
        assert list(project.clips.values_list("sequence_number", flat=True)) == [
            1,
            2,
            3,
            4,
            5,
        ]

    def test_create_project_saves_all_fields(self, client):
        """Should store all form fields on the project."""
        client.post(
            "/projects/new/",
            {
                "title": "Full Fields",
                "description": "All fields test",
                "visual_style": "Dark moody tones",
                "aspect_ratio": "16:9",
                "clip_duration": "4",
                "num_clips": "10",
            },
        )
        project = Project.objects.get(title="Full Fields")
        assert project.visual_style == "Dark moody tones"
        assert project.aspect_ratio == "16:9"
        assert project.clip_duration == 4
        assert project.num_clips == 10

    def test_create_project_requires_title(self, client):
        """Should return validation error when title is missing."""
        response = client.post(
            "/projects/new/",
            {
                "title": "",
                "description": "No title given.",
                "aspect_ratio": "9:16",
                "clip_duration": "8",
                "num_clips": "7",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "Title is required" in content
        assert Project.objects.count() == 0

    def test_create_project_requires_description(self, client):
        """Should return validation error when description is missing."""
        response = client.post(
            "/projects/new/",
            {
                "title": "Has Title",
                "description": "",
                "aspect_ratio": "9:16",
                "clip_duration": "8",
                "num_clips": "7",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "Description is required" in content
        assert Project.objects.count() == 0

    def test_form_get_prefills_user_settings_defaults(self, client, db):
        """Should prefill form defaults from UserSettings when available."""
        settings = UserSettings.load()
        settings.default_aspect_ratio = "16:9"
        settings.default_clip_duration = 4
        settings.default_num_clips = 6
        settings.default_visual_style = "Warm tones"
        settings.save()

        response = client.get("/projects/new/")
        content = response.content.decode()
        assert "Warm tones" in content


@pytest.mark.django_db
class TestDeleteProject:
    """Verify project deletion via the AJAX API."""

    def test_delete_project_returns_200(self, client, sample_project):
        """Should return 200 and delete the project."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/delete/",
            content_type="application/json",
        )
        assert response.status_code == 200
        assert not Project.objects.filter(pk=sample_project.pk).exists()

    def test_delete_project_cascades_clips(self, client, sample_project):
        """Should delete all clips when project is deleted."""
        clip_count_before = Clip.objects.filter(project=sample_project).count()
        assert clip_count_before > 0

        client.post(
            f"/api/projects/{sample_project.pk}/delete/",
            content_type="application/json",
        )
        assert Clip.objects.filter(project=sample_project).count() == 0

    def test_delete_project_cascades_references(self, client, sample_project_with_ref):
        """Should delete reference images when project is deleted."""
        project = sample_project_with_ref
        assert project.reference_images.count() == 1

        client.post(
            f"/api/projects/{project.pk}/delete/",
            content_type="application/json",
        )
        assert ReferenceImage.objects.filter(project=project).count() == 0

    def test_delete_nonexistent_project_returns_404(self, client, db):
        """Should return 404 for a project that does not exist."""
        response = client.post(
            "/api/projects/99999/delete/",
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_delete_only_accepts_post(self, client, sample_project):
        """Should reject GET requests."""
        response = client.get(
            f"/api/projects/{sample_project.pk}/delete/",
        )
        assert response.status_code == 405


@pytest.mark.django_db
class TestRenameProject:
    """Verify project renaming via the AJAX API."""

    def test_rename_project_returns_200(self, client, sample_project):
        """Should rename the project and return the new title."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/rename/",
            data=json.dumps({"title": "Renamed Project"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Renamed Project"

        sample_project.refresh_from_db()
        assert sample_project.title == "Renamed Project"

    def test_rename_project_rejects_empty_title(self, client, sample_project):
        """Should return 400 when title is empty."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/rename/",
            data=json.dumps({"title": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_rename_project_rejects_long_title(self, client, sample_project):
        """Should return 400 when title exceeds 100 characters."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/rename/",
            data=json.dumps({"title": "A" * 101}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_rename_project_rejects_invalid_json(self, client, sample_project):
        """Should return 400 for malformed JSON body."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/rename/",
            data="not json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_rename_nonexistent_project_returns_404(self, client, db):
        """Should return 404 for a project that does not exist."""
        response = client.post(
            "/api/projects/99999/rename/",
            data=json.dumps({"title": "Ghost"}),
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestDuplicateProject:
    """Verify project duplication via the AJAX API."""

    def test_duplicate_project_returns_200(self, client, sample_project):
        """Should create a duplicate and return its ID and title."""
        response = client.post(
            f"/api/projects/{sample_project.pk}/duplicate/",
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["new_title"] == "Test Project (Copy)"
        assert Project.objects.count() == 2

    def test_duplicate_copies_metadata(self, client, sample_project):
        """Should copy all project metadata to the duplicate."""
        client.post(
            f"/api/projects/{sample_project.pk}/duplicate/",
            content_type="application/json",
        )
        duplicate = Project.objects.get(title="Test Project (Copy)")
        assert duplicate.description == sample_project.description
        assert duplicate.visual_style == sample_project.visual_style
        assert duplicate.aspect_ratio == sample_project.aspect_ratio
        assert duplicate.clip_duration == sample_project.clip_duration
        assert duplicate.num_clips == sample_project.num_clips

    def test_duplicate_copies_clip_scripts(self, client, sample_project):
        """Should copy all clip scripts without video files."""
        client.post(
            f"/api/projects/{sample_project.pk}/duplicate/",
            content_type="application/json",
        )
        duplicate = Project.objects.get(title="Test Project (Copy)")
        assert duplicate.clips.count() == sample_project.clips.count()
        for original, copy in zip(sample_project.clips.all(), duplicate.clips.all()):
            assert copy.script_text == original.script_text
            assert copy.sequence_number == original.sequence_number
            assert not copy.video_file

    def test_duplicate_does_not_copy_videos(self, client, sample_project):
        """Should not copy video files in the duplicated clips."""
        client.post(
            f"/api/projects/{sample_project.pk}/duplicate/",
            content_type="application/json",
        )
        duplicate = Project.objects.get(title="Test Project (Copy)")
        for clip in duplicate.clips.all():
            assert clip.generation_status == "idle"
            assert not clip.video_file.name

    def test_duplicate_nonexistent_project_returns_404(self, client, db):
        """Should return 404 for a project that does not exist."""
        response = client.post(
            "/api/projects/99999/duplicate/",
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestSearchBehavior:
    """Verify search bar filtering renders properly client-side.

    Search is client-side jQuery filtering, so we test that the data
    attributes required for filtering are present in the rendered HTML.
    """

    def test_project_cards_have_data_title_attribute(self, client, multiple_projects):
        """Should render data-title attribute for client-side filtering."""
        response = client.get("/")
        content = response.content.decode()
        for project in multiple_projects:
            assert f'data-title="{project.title}"' in content

    def test_search_input_is_enabled_when_projects_exist(
        self, client, multiple_projects
    ):
        """Should render the search input without disabled attribute."""
        response = client.get("/")
        content = response.content.decode()
        assert 'class="form-input search-bar__input js-search-input"' in content
        # The input should not have 'disabled' attribute
        search_section = content[
            content.index("js-search-input") : content.index("js-search-input") + 200
        ]
        assert "disabled" not in search_section
