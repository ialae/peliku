"""Django forms for the core app."""

from django import forms

from core.models import (
    ASPECT_RATIO_CHOICES,
    CLIP_DURATION_CHOICES,
)

NUM_CLIPS_CHOICES = [
    (5, "5 clips"),
    (6, "6 clips"),
    (7, "7 clips"),
    (8, "8 clips"),
    (9, "9 clips"),
    (10, "10 clips"),
]

MIN_NUM_CLIPS = 5
MAX_NUM_CLIPS = 10
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 2000
MAX_VISUAL_STYLE_LENGTH = 500


class ProjectForm(forms.Form):
    """Validates input for creating a new reel project.

    Fields mirror the Project model constraints: title and description
    are required, visual_style is optional, and the remaining fields
    are constrained to specific choices.
    """

    title = forms.CharField(
        max_length=MAX_TITLE_LENGTH,
        required=True,
        error_messages={
            "required": "Title is required.",
            "max_length": "Title must be 100 characters or fewer.",
        },
    )
    description = forms.CharField(
        max_length=MAX_DESCRIPTION_LENGTH,
        required=True,
        widget=forms.Textarea,
        error_messages={
            "required": "Description is required.",
            "max_length": "Description must be 2,000 characters or fewer.",
        },
    )
    visual_style = forms.CharField(
        max_length=MAX_VISUAL_STYLE_LENGTH,
        required=False,
        widget=forms.Textarea,
        error_messages={
            "max_length": "Visual style must be 500 characters or fewer.",
        },
    )
    aspect_ratio = forms.ChoiceField(
        choices=ASPECT_RATIO_CHOICES,
        initial="9:16",
        error_messages={
            "invalid_choice": "Invalid aspect ratio.",
        },
    )
    clip_duration = forms.TypedChoiceField(
        choices=CLIP_DURATION_CHOICES,
        coerce=int,
        initial=8,
        error_messages={
            "invalid_choice": "Clip duration must be 4, 6, or 8.",
        },
    )
    num_clips = forms.TypedChoiceField(
        choices=NUM_CLIPS_CHOICES,
        coerce=int,
        initial=7,
        error_messages={
            "invalid_choice": "Number of clips must be between 5 and 10.",
        },
    )
