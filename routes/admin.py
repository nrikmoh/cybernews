# routes/admin.py
# ─────────────────────────────────────────────────────────
# Admin routes for managing CyberNews content.
#
# Routes:
#   GET  /admin                    → dashboard
#   GET  /admin/articles           → list articles
#   GET  /admin/articles/new       → show add form
#   POST /admin/articles/new       → process add form
#   GET  /admin/articles/edit/<id> → show edit form
#   POST /admin/articles/edit/<id> → process edit form
#   POST /admin/articles/delete/<id> → delete article
# ─────────────────────────────────────────────────────────

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from models  import db, Article, Category, Newsletter
from forms   import ArticleForm, DeleteForm
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
#                                        ↑
# url_prefix means ALL routes in this blueprint
# automatically start with /admin
# So @admin_bp.route('/') becomes /admin/
# And @admin_bp.route('/articles') becomes /admin/articles


# ─────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────
@admin_bp.route('/')
def dashboard():
    """
    Admin overview page showing site statistics.
    """

    # Gather statistics for the dashboard
    stats = {
        'total_articles':     Article.query.count(),
        'published_articles': Article.query.filter_by(published=True).count(),
        'draft_articles':     Article.query.filter_by(published=False).count(),
        'featured_articles':  Article.query.filter_by(featured=True).count(),
        'total_subscribers':  Newsletter.query.filter_by(active=True).count(),
        'total_categories':   len([
            c for c in [
                'Malware', 'Data Breaches', 'Vulnerabilities',
                'Privacy', 'Research', 'Threats'
            ]
        ]),
    }

    # Category breakdown
    categories_data = []
    for cat_name in ['Malware', 'Data Breaches', 'Vulnerabilities',
                     'Privacy', 'Research', 'Threats']:
        count = Article.query.filter_by(category=cat_name).count()
        categories_data.append({'name': cat_name, 'count': count})

    # Recent articles
    recent = Article.query.order_by(
        Article.created_at.desc()
    ).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats           = stats,
        categories_data = categories_data,
        recent          = recent,
    )


# ─────────────────────────────────────────
# LIST ALL ARTICLES
# ─────────────────────────────────────────
@admin_bp.route('/articles')
def articles_list():
    """Show all articles in a management table."""

    # Optional: filter by category or status
    category = request.args.get('category', '')
    status   = request.args.get('status', '')

    query = Article.query

    if category:
        query = query.filter_by(category=category)

    if status == 'published':
        query = query.filter_by(published=True)
    elif status == 'draft':
        query = query.filter_by(published=False)
    elif status == 'featured':
        query = query.filter_by(featured=True)

    articles = query.order_by(Article.created_at.desc()).all()

    # Create a delete form for each article (for CSRF protection)
    delete_form = DeleteForm()

    return render_template(
        'admin/articles_list.html',
        articles    = articles,
        delete_form = delete_form,
        filter_category = category,
        filter_status   = status,
    )


# ─────────────────────────────────────────
# ADD NEW ARTICLE
# ─────────────────────────────────────────
@admin_bp.route('/articles/new', methods=['GET', 'POST'])
def article_new():
    """
    GET:  Show the empty article form.
    POST: Validate and save the new article.
    
    This route handles BOTH showing and processing the form.
    Flask knows which one by checking request.method.
    """

    form = ArticleForm()

    # form.validate_on_submit() returns True only when:
    # 1. The request method is POST, AND
    # 2. All validators pass
    if form.validate_on_submit():

        # If user checked "featured", unset any existing featured article
        # (only one article should be featured at a time)
        if form.featured.data:
            Article.query.filter_by(featured=True).update({'featured': False})
            db.session.commit()

        # Create new Article object from form data
        article = Article(
            title      = form.title.data.strip(),
            summary    = form.summary.data.strip(),
            body       = form.body.data.strip(),
            category   = form.category.data,
            source     = form.source.data.strip(),
            image_url  = form.image_url.data or
                        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
            featured   = form.featured.data,
            published  = form.published.data,
            tags_string = form.tags_string.data.strip(),
        )

        # Save to database
        db.session.add(article)
        db.session.commit()

        # flash() sends a one-time message to the next page
        # 'success' is the category (used for styling)
        flash(f'✅ Article "{article.title[:50]}..." added successfully!', 'success')

        # PRG Pattern: redirect after POST
        # This prevents double-submission on page refresh
        return redirect(url_for('admin.articles_list'))

    # If GET request OR validation failed: show the form
    # (If validation failed, form object contains error messages)
    return render_template(
        'admin/article_form.html',
        form       = form,
        form_title = 'Add New Article',
        form_action = url_for('admin.article_new'),
    )


# ─────────────────────────────────────────
# EDIT ARTICLE
# ─────────────────────────────────────────
@admin_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
def article_edit(article_id):
    """
    GET:  Show form pre-filled with existing article data.
    POST: Validate and update the article.
    """

    article = db.get_or_404(Article, article_id)

    # obj=article pre-fills the form with existing data
    form = ArticleForm(obj=article)

    if form.validate_on_submit():

        # Handle featured: if setting this as featured,
        # remove featured from all others first
        if form.featured.data and not article.featured:
            Article.query.filter(
                Article.featured == True,
                Article.id       != article_id,
            ).update({'featured': False})
            db.session.commit()

        # Update the article fields
        article.title       = form.title.data.strip()
        article.summary     = form.summary.data.strip()
        article.body        = form.body.data.strip()
        article.category    = form.category.data
        article.source      = form.source.data.strip()
        article.featured    = form.featured.data
        article.published   = form.published.data
        article.tags_string = form.tags_string.data.strip()
        article.updated_at  = datetime.utcnow()

        # Only update image if a new one was provided
        if form.image_url.data:
            article.image_url = form.image_url.data

        db.session.commit()

        flash(f'✅ Article updated successfully!', 'success')
        return redirect(url_for('admin.articles_list'))

    return render_template(
        'admin/article_form.html',
        form        = form,
        article     = article,
        form_title  = f'Edit Article #{article_id}',
        form_action = url_for('admin.article_edit', article_id=article_id),
    )


# ─────────────────────────────────────────
# DELETE ARTICLE
# ─────────────────────────────────────────
@admin_bp.route('/articles/delete/<int:article_id>', methods=['POST'])
def article_delete(article_id):
    """
    Delete an article from the database.
    
    Only accepts POST — never GET.
    (You should never delete data with a GET request,
    because GET requests can be triggered by just visiting a URL,
    clicking a link, or even a browser pre-fetching pages.)
    """

    article = db.get_or_404(Article, article_id)

    # Verify CSRF token via the form
    form = DeleteForm()
    if not form.validate_on_submit():
        flash('❌ Invalid request. Please try again.', 'error')
        return redirect(url_for('admin.articles_list'))

    title = article.title[:50]

    db.session.delete(article)
    db.session.commit()

    flash(f'🗑️ Article "{title}..." deleted.', 'warning')
    return redirect(url_for('admin.articles_list'))


# ─────────────────────────────────────────
# TOGGLE PUBLISH STATUS (quick action)
# ─────────────────────────────────────────
@admin_bp.route('/articles/toggle/<int:article_id>', methods=['POST'])
def article_toggle(article_id):
    """
    Quickly toggle an article between published and draft
    without opening the full edit form.
    """
    article          = db.get_or_404(Article, article_id)
    article.published = not article.published
    db.session.commit()

    status = 'published' if article.published else 'saved as draft'
    flash(f'Article {status}.', 'success')
    return redirect(url_for('admin.articles_list'))


# ─────────────────────────────────────────
# NEWSLETTER SUBSCRIBERS
# ─────────────────────────────────────────
@admin_bp.route('/subscribers')
def subscribers():
    """List all newsletter subscribers."""
    subs = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
    return render_template('admin/subscribers.html', subscribers=subs)
