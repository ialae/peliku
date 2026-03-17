"""URL configuration for the core app."""

from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/new/", views.project_form, name="project_form"),
]
