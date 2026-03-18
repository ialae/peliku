"""Gemini AI client initialization and access."""

import logging

from google import genai

from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def get_ai_client():
    """Return a singleton Gemini client instance.

    Initializes the client on first call using GEMINI_API_KEY
    from Django settings. Subsequent calls return the same instance.

    Returns:
        genai.Client: Configured Gemini API client.

    Raises:
        ValueError: If GEMINI_API_KEY is not configured.
    """
    global _client  # noqa: PLW0603
    if _client is None:
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file to use AI features."
            )
        _client = genai.Client(api_key=api_key)
        logger.info("Gemini AI client initialized")
    return _client


def reset_client():
    """Reset the singleton client (used in testing)."""
    global _client  # noqa: PLW0603
    _client = None
