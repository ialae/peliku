"""Views for the core app."""

from django.shortcuts import render


def home(request):
    """Render the home page with the project dashboard."""
    return render(request, "core/home.html")


def project_form(request):
    """Render the new-project form page."""
    return render(request, "core/project_form.html")
