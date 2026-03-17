"""Management command to seed the database with sample development data."""

from django.core.management.base import BaseCommand

from core.models import Clip, Project, ReferenceImage, UserSettings

SAMPLE_PROJECTS = [
    {
        "title": "Golden Hour Coastline",
        "description": (
            "A cinematic reel capturing the magic of golden hour along "
            "a rugged coastline. Waves crash against weathered cliffs as "
            "seabirds glide overhead. The camera follows a lone figure "
            "walking toward a lighthouse at the edge of the world."
        ),
        "visual_style": (
            "Cinematic film grain, warm golden-hour tones, " "shallow depth of field"
        ),
        "aspect_ratio": "9:16",
        "clip_duration": 8,
        "num_clips": 7,
    },
    {
        "title": "Neon City Nights",
        "description": (
            "A high-energy reel set in a futuristic cityscape at night. "
            "Neon signs reflect off rain-slicked streets. Street vendors, "
            "holographic billboards, and speeding hover-taxis paint a "
            "vibrant portrait of urban life in 2087."
        ),
        "visual_style": "Cyberpunk neon palette, high contrast, moody reflections",
        "aspect_ratio": "9:16",
        "clip_duration": 6,
        "num_clips": 7,
    },
    {
        "title": "Mountain Sunrise Trek",
        "description": (
            "A peaceful reel following a solo hiker ascending a misty "
            "mountain trail at dawn. Fog drifts through ancient pine "
            "forests. As the sun breaks over the summit, the world "
            "below is revealed in breathtaking detail."
        ),
        "visual_style": "Natural light, muted earth tones, documentary feel",
        "aspect_ratio": "16:9",
        "clip_duration": 8,
        "num_clips": 5,
    },
]

CLIP_SCRIPTS = [
    "A sweeping aerial shot reveals the landscape at dawn. Morning mist "
    "clings to the valleys below as warm light breaks through scattered clouds.",
    "The camera pushes forward along a winding path. Dew glistens on tall "
    "grass as a gentle breeze carries scattered petals across the frame.",
    "A close-up captures weathered hands adjusting a leather strap. The "
    "subject pauses, gazing at the horizon with quiet determination.",
    "Wide shot of the subject walking through an open meadow. Wildflowers "
    "sway in rhythmic patterns. Soft ambient music builds underneath.",
    "The camera drifts upward, revealing a vast panorama. Mountains stretch "
    "to the edge of the frame. A hawk circles lazily in the thermal currents.",
    "Medium shot at eye level as the subject reaches a stone overlook. Wind "
    "tousles their hair. They smile, taking in the view for the first time.",
    "Final wide shot as the sun dips below the ridge. Long shadows stretch "
    "across the terrain. The scene fades to warm amber, then to black.",
]

REFERENCE_LABELS = [
    "Main character — weathered explorer with leather jacket",
    "Landscape anchor — misty mountain ridge at sunrise",
    "Key prop — vintage brass compass with cracked glass",
]


class Command(BaseCommand):
    """Seed the database with sample projects, clips, and settings."""

    help = "Create sample development data for testing"

    def handle(self, *args, **options):
        """Execute the seed command."""
        self._seed_user_settings()
        self._seed_projects()
        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))

    def _seed_user_settings(self):
        """Ensure a UserSettings singleton row exists."""
        UserSettings.load()
        self.stdout.write("  UserSettings singleton ensured.")

    def _seed_projects(self):
        """Create sample projects with clips and one reference image each."""
        for project_data in SAMPLE_PROJECTS:
            project, created = Project.objects.get_or_create(
                title=project_data["title"],
                defaults=project_data,
            )
            if not created:
                self.stdout.write(
                    f"  Project '{project.title}' already exists — skipped."
                )
                continue

            for seq in range(1, project.num_clips + 1):
                script_index = (seq - 1) % len(CLIP_SCRIPTS)
                Clip.objects.create(
                    project=project,
                    sequence_number=seq,
                    script_text=CLIP_SCRIPTS[script_index],
                )

            label_index = SAMPLE_PROJECTS.index(project_data) % len(REFERENCE_LABELS)
            ReferenceImage.objects.create(
                project=project,
                slot_number=1,
                image_file="images/references/placeholder.png",
                label=REFERENCE_LABELS[label_index],
            )

            self.stdout.write(f"  Created project '{project.title}' with clips.")
