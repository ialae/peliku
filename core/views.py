"""Views for the core app."""

from django.shortcuts import render


def home(request):
    """Render the home page with the project dashboard."""
    return render(request, "core/home.html")


def project_form(request):
    """Render the new-project form page."""
    return render(request, "core/project_form.html")


def workspace(request, project_id):
    """Render the Project Workspace page with dummy clip data.

    Displays a shell layout with static placeholder clips, a compact
    header bar, and a collapsible Reference Images Panel.  Real data
    will be wired in Sprint 8+.
    """
    dummy_clips = [
        {
            "number": i,
            "script": (
                f"Clip {i} — A sweeping aerial shot reveals the "
                "sun-drenched coastline at golden hour. Warm amber "
                "light bathes the rocky cliffs as seabirds glide "
                "through the frame. The camera slowly pushes forward "
                "toward a lone lighthouse perched on the headland."
            ),
        }
        for i in range(1, 4)
    ]

    context = {
        "project": {
            "id": project_id,
            "title": "Untitled Project",
            "description": "A short reel about nature and adventure.",
            "aspect_ratio": "9:16",
            "clip_duration": 8,
            "visual_style": "Cinematic, warm golden-hour tones",
        },
        "clips": dummy_clips,
    }
    return render(request, "core/workspace.html", context)
