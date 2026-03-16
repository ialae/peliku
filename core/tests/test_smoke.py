"""Smoke tests for the core app."""

import pytest
from django.test import Client


@pytest.mark.django_db
def test_home_page_returns_200():
    """Should return 200 when visiting the home page."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_contains_reelforge():
    """Should contain 'ReelForge' text on the home page."""
    client = Client()
    response = client.get("/")
    assert b"ReelForge" in response.content
