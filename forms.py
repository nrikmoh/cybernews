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
    """
    Form for creating and editing news articles.
    
    FlaskForm automatically adds CSRF protection —
    a hidden token in the form that prevents
    Cross-Site Request Forgery attacks.
    """

    # ── Title ──────────────────────────────────────────
    title = StringField(
        label      = 'Article Title',
        validators = [
            # DataRequired: field cannot be empty
            DataRequired(message='Title is required.'),
            # Length: must be between 10 and 300 characters
            Length(
                min     = 10,
                max     = 300,
                message = 'Title must be between 10 and 300 characters.'
            ),
        ],
        render_kw = {
            'placeholder': 'e.g. Critical Zero-Day Found in Windows Kernel',
            'class':       'form-input',
        }
    )

    # ── Summary ────────────────────────────────────────
    summary = TextAreaField(
        label      = 'Short Summary',
        validators = [
            DataRequired(message='Summary is required.'),
            Length(
                min     = 20,
                max     = 500,
                message = 'Summary must be between 20 and 500 characters.'
            ),
        ],
        render_kw = {
            'placeholder': 'A brief description shown on article cards (2-3 sentences)',
            'class':       'form-input',
            'rows':        '3',
        }
    )

    # ── Body ───────────────────────────────────────────
    body = TextAreaField(
        label      = 'Full Article Body',
        validators = [
            DataRequired(message='Article body is required.'),
            Length(
                min     = 50,
                message = 'Article body must be at least 50 characters.'
            ),
        ],
        render_kw = {
            'placeholder': 'Write the full article here. Separate paragraphs with blank lines.',
            'class':       'form-input form-textarea',
            'rows':        '15',
        }
    )

    # ── Category ───────────────────────────────────────
    # SelectField creates a dropdown menu
    category = SelectField(
        label      = 'Category',
        validators = [DataRequired(message='Please select a category.')],
        choices    = [
            # ('value stored in DB', 'Label shown to user')
            ('',               'Select a category...'),
            ('Malware',        '🦠 Malware'),
            ('Data Breaches',  '💾 Data Breaches'),
            ('Vulnerabilities','⚠️  Vulnerabilities'),
            ('Privacy',        '🔒 Privacy'),
            ('Research',       '🔬 Research'),
            ('Threats',        '🎯 Threats'),
        ],
        render_kw = {'class': 'form-input form-select'}
    )

    # ── Source ─────────────────────────────────────────
    source = StringField(
        label      = 'News Source',
        validators = [
            DataRequired(message='Source is required.'),
            Length(max=100),
        ],
        render_kw = {
            'placeholder': 'e.g. The Hacker News, SecurityWeek',
            'class':       'form-input',
            'list':        'sources-list',  # links to HTML datalist
        }
    )

    # ── Image URL ──────────────────────────────────────
    image_url = URLField(
        label      = 'Image URL',
        validators = [
            Optional(),       # This field is not required
            URL(message='Please enter a valid URL starting with http:// or https://')
        ],
        render_kw = {
            'placeholder': 'https://images.unsplash.com/...',
            'class':       'form-input',
        }
    )

    # ── Tags ───────────────────────────────────────────
    tags_string = StringField(
        label      = 'Tags',
        validators = [Optional(), Length(max=300)],
        render_kw  = {
            'placeholder': 'Windows, Zero-Day, CVE, Microsoft (comma-separated)',
            'class':       'form-input',
        }
    )

    # ── Checkboxes ─────────────────────────────────────
    featured = BooleanField(
        label     = 'Feature this article (shows as hero story)',
        render_kw = {'class': 'form-checkbox'}
    )

    published = BooleanField(
        label     = 'Published (visible to public)',
        default   = True,
        render_kw = {'class': 'form-checkbox'}
    )

    # ── Submit Button ──────────────────────────────────
    submit = SubmitField(
        label     = 'Save Article',
        render_kw = {'class': 'btn-submit'}
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
