"""Tests for the global layout: base template, CSS links, header, jQuery."""

import pytest

from django.test import Client


@pytest.mark.django_db
class TestBaseLayout:
    """Verify base template renders correct structure and assets."""

    def setup_method(self):
        """Set up a test client for each test."""
        self.client = Client()

    def test_page_contains_reelforge_brand(self):
        """Should render the ReelForge brand name in the header."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "ReelForge" in content

    def test_page_loads_css_reset(self):
        """Should include reset.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "reset.css" in content

    def test_page_loads_css_tokens(self):
        """Should include tokens.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "tokens.css" in content

    def test_page_loads_css_typography(self):
        """Should include typography.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "typography.css" in content

    def test_page_loads_css_layout(self):
        """Should include layout.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "layout.css" in content

    def test_page_loads_css_components(self):
        """Should include components.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "components.css" in content

    def test_page_loads_css_animations(self):
        """Should include animations.css link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "animations.css" in content

    def test_page_loads_jquery(self):
        """Should include jQuery script tag."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "jquery" in content.lower()

    def test_page_loads_main_js(self):
        """Should include main.js script tag."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "main.js" in content

    def test_header_nav_is_present(self):
        """Should render the site header element."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="site-header"' in content

    def test_header_contains_logo_link(self):
        """Should render a logo link in the header."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="site-header__logo"' in content

    def test_header_contains_settings_button(self):
        """Should render the settings gear button."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "js-settings-toggle" in content

    def test_toast_container_is_present(self):
        """Should render the toast notification container."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'id="toast-container"' in content

    def test_phosphor_icons_loaded(self):
        """Should include the Phosphor Icons CDN link."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "phosphor-icons" in content

    def test_google_fonts_loaded(self):
        """Should include Google Fonts links."""
        response = self.client.get("/")
        content = response.content.decode()
        assert "fonts.googleapis.com" in content

    def test_main_content_area_present(self):
        """Should render the main content area with container."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="main-content"' in content
        assert 'class="container"' in content
