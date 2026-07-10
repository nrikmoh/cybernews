# routes/admin.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import login_required, current_user
from models      import db, Article, Category, Newsletter
from forms       import ArticleForm, DeleteForm
from datetime    import datetime
from security import log_admin_action, sanitize_string, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────
@admin_bp.route('/')
@login_required          # ← This is all it takes to protect a route!
def dashboard():
    stats = {
        'total_articles':     Article.query.count(),
        'published_articles': Article.query.filter_by(published=True).count(),
        'draft_articles':     Article.query.filter_by(published=False).count(),
        'featured_articles':  Article.query.filter_by(featured=True).count(),
        'total_subscribers':  Newsletter.query.filter_by(active=True).count(),
        'total_categories':   6,
    }

    categories_data = []
    for cat_name in ['Malware', 'Data Breaches', 'Vulnerabilities',
                     'Privacy', 'Research', 'Threats']:
        count = Article.query.filter_by(category=cat_name).count()
        categories_data.append({'name': cat_name, 'count': count})

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
@login_required
def articles_list():
    category = request.args.get('category', '')
    status   = request.args.get('status', '')
    query    = Article.query

    if category:
        query = query.filter_by(category=category)
    if status == 'published':
        query = query.filter_by(published=True)
    elif status == 'draft':
        query = query.filter_by(published=False)
    elif status == 'featured':
        query = query.filter_by(featured=True)

    articles    = query.order_by(Article.created_at.desc()).all()
    delete_form = DeleteForm()

    return render_template(
        'admin/articles_list.html',
        articles        = articles,
        delete_form     = delete_form,
        filter_category = category,
        filter_status   = status,
    )


# ─────────────────────────────────────────
# ADD NEW ARTICLE
# ─────────────────────────────────────────
@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
def article_new():
    form = ArticleForm()

    if form.validate_on_submit():
        if form.featured.data:
            Article.query.filter_by(featured=True).update({'featured': False})
            db.session.commit()

        article = Article(
            title       = sanitize_string(form.title.data, 300),
            summary     = sanitize_string(form.summary.data, 500),
            body        = form.body.data.strip(),
            category    = form.category.data,
            source      = sanitize_string(form.source.data, 100),
            image_url   = form.image_url.data or
                         'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
            featured    = form.featured.data,
            published   = form.published.data,
            tags_string = sanitize_string(form.tags_string.data, 300),
        )
        db.session.add(article)
        db.session.commit()

        # Log this admin action
        log_admin_action('CREATE_ARTICLE', f'ID:{article.id} Title:{article.title[:50]}')

        flash('✅ Article added successfully!', 'success')
        return redirect(url_for('admin.articles_list'))

    return render_template(
        'admin/article_form.html',
        form        = form,
        form_title  = 'Add New Article',
        form_action = url_for('admin.article_new'),
    )

# ─────────────────────────────────────────
# EDIT ARTICLE
# ─────────────────────────────────────────
@admin_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def article_edit(article_id):
    article = db.get_or_404(Article, article_id)
    form    = ArticleForm(obj=article)

    if form.validate_on_submit():
        if form.featured.data and not article.featured:
            Article.query.filter(
                Article.featured == True,
                Article.id       != article_id,
            ).update({'featured': False})
            db.session.commit()

        article.title       = form.title.data.strip()
        article.summary     = form.summary.data.strip()
        article.body        = form.body.data.strip()
        article.category    = form.category.data
        article.source      = form.source.data.strip()
        article.featured    = form.featured.data
        article.published   = form.published.data
        article.tags_string = form.tags_string.data.strip()
        article.updated_at  = datetime.utcnow()

        if form.image_url.data:
            article.image_url = form.image_url.data

        db.session.commit()
        flash('✅ Article updated successfully!', 'success')
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
@login_required
def article_delete(article_id):
    article = db.get_or_404(Article, article_id)
    form    = DeleteForm()

    if not form.validate_on_submit():
        flash('❌ Invalid request.', 'error')
        return redirect(url_for('admin.articles_list'))

    title = article.title[:50]

    # Log before deleting
    log_admin_action('DELETE_ARTICLE', f'ID:{article_id} Title:{title}')

    db.session.delete(article)
    db.session.commit()

    flash(f'🗑️ Article "{title}..." deleted.', 'warning')
    return redirect(url_for('admin.articles_list'))

# ─────────────────────────────────────────
# TOGGLE PUBLISH
# ─────────────────────────────────────────
@admin_bp.route('/articles/toggle/<int:article_id>', methods=['POST'])
@login_required
def article_toggle(article_id):
    article           = db.get_or_404(Article, article_id)
    article.published = not article.published
    db.session.commit()

    status = 'published' if article.published else 'saved as draft'
    flash(f'Article {status}.', 'success')
    return redirect(url_for('admin.articles_list'))


# ─────────────────────────────────────────
# SUBSCRIBERS
# ─────────────────────────────────────────
@admin_bp.route('/subscribers')
@login_required
def subscribers():
    subs = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
    return render_template('admin/subscribers.html', subscribers=subs)

# ─────────────────────────────────────────
# LOGIN AUDIT LOG
# ─────────────────────────────────────────
@admin_bp.route('/security')
@login_required
def security_log():
    """View recent login attempts — security monitoring."""
    from models import LoginLog

    logs = LoginLog.query.order_by(
        LoginLog.timestamp.desc()
    ).limit(50).all()

    # Count stats
    total    = len(logs)
    failed   = sum(1 for l in logs if not l.success)
    success  = total - failed

    return render_template(
        'admin/security_log.html',
        logs    = logs,
        total   = total,
        failed  = failed,
        success = success,
    )
