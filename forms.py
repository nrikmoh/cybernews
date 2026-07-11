# forms.py
# ─────────────────────────────────────────────────────────
# WTForms form definitions for CyberNews.
#
# Each class = one HTML form.
# Each attribute = one form field.
# Validators = rules the submitted data must follow.
# ─────────────────────────────────────────────────────────

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    BooleanField,
    URLField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    URL,
)


# ═══════════════════════════════════════════════════════
# ARTICLE FORM
# Used for both adding AND editing articles.
# ═══════════════════════════════════════════════════════
class ArticleForm(FlaskForm):
    """Form for creating and editing news articles."""

    title = StringField(
        label='Article Title',
        validators=[
            DataRequired(message='Title is required.'),
            Length(min=10, max=300,
                   message='Title must be between 10 and 300 characters.'),
        ],
        render_kw={
            'placeholder': 'e.g. Critical Zero-Day Found in Windows Kernel',
            'class': 'form-input',
            'maxlength': '300',
        }
    )

    summary = TextAreaField(
        label='Short Summary',
        validators=[
            DataRequired(message='Summary is required.'),
            Length(min=20, max=500,
                   message='Summary must be between 20 and 500 characters.'),
        ],
        render_kw={
            'placeholder': 'Brief description (2-3 sentences)',
            'class': 'form-input',
            'rows': '3',
            'maxlength': '500',
        }
    )

    body = TextAreaField(
        label='Full Article Body',
        validators=[
            DataRequired(message='Article body is required.'),
            Length(min=50, message='Body must be at least 50 characters.'),
        ],
        render_kw={
            'placeholder': 'Full article text. Separate paragraphs with blank lines.',
            'class': 'form-input form-textarea',
            'rows': '15',
        }
    )

    category = SelectField(
        label='Category',
        validators=[DataRequired(message='Please select a category.')],
        choices=[
            ('',               'Select a category...'),
            ('Malware',        '🦠 Malware'),
            ('Data Breaches',  '💾 Data Breaches'),
            ('Vulnerabilities','⚠️ Vulnerabilities'),
            ('Privacy',        '🔒 Privacy'),
            ('Research',       '🔬 Research'),
            ('Threats',        '🎯 Threats'),
        ],
        render_kw={'class': 'form-input form-select'}
    )

    source = StringField(
        label='News Source',
        validators=[
            DataRequired(message='Source is required.'),
            Length(max=100, message='Source too long.'),
        ],
        render_kw={
            'placeholder': 'e.g. The Hacker News, SecurityWeek',
            'class': 'form-input',
            'list': 'sources-list',
            'maxlength': '100',
        }
    )

    image_url = URLField(
        label='Image URL',
        validators=[
            Optional(),
            URL(require_tld=True,
                message='Please enter a valid URL starting with https://')
        ],
        render_kw={
            'placeholder': 'https://images.unsplash.com/...',
            'class': 'form-input',
        }
    )

    tags_string = StringField(
        label='Tags',
        validators=[Optional(), Length(max=300)],
        render_kw={
            'placeholder': 'Windows, Zero-Day, CVE (comma-separated)',
            'class': 'form-input',
            'maxlength': '300',
        }
    )

    featured = BooleanField(
        label='Feature this article (shows as hero story)',
        render_kw={'class': 'form-checkbox'}
    )

    published = BooleanField(
        label='Published (visible to public)',
        default=True,
        render_kw={'class': 'form-checkbox'}
    )

    submit = SubmitField(
        label='Save Article',
        render_kw={'class': 'btn-submit'}
    )



# ═══════════════════════════════════════════════════════
# DELETE CONFIRMATION FORM
# A minimal form just to confirm deletion.
# Having a form (not just a link) prevents accidental
# deletion and provides CSRF protection.
# ═══════════════════════════════════════════════════════
class DeleteForm(FlaskForm):
    """
    Empty form used only for CSRF protection on delete actions.
    The submit button is all we need.
    """
    submit = SubmitField(
        label     = 'Yes, Delete Article',
        render_kw = {'class': 'btn-danger'}
    )
