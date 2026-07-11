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
@login_required
def dashboard():
    from models import PageView

    stats = {
        'total_articles':     Article.query.count(),
        'published_articles': Article.query.filter_by(published=True).count(),
        'draft_articles':     Article.query.filter_by(published=False).count(),
        'featured_articles':  Article.query.filter_by(featured=True).count(),
        'total_subscribers':  Newsletter.query.filter_by(active=True).count(),
        'total_categories':   6,
        'total_views':        PageView.total_views(),
        'unique_visitors':    PageView.unique_visitors(),
        'today_views':        PageView.today_views(),
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

# ─────────────────────────────────────────
# MANUAL RSS FETCH TRIGGER
# ─────────────────────────────────────────
@admin_bp.route('/fetch-news', methods=['POST'])
@login_required
def fetch_news():
    """
    Manually trigger an RSS fetch from the admin panel.
    Useful for getting fresh content without waiting for cron.
    """
    try:
        import subprocess
        import sys

        # Run the fetcher as a subprocess
        result = subprocess.run(
            [sys.executable, 'rss_fetcher.py'],
            capture_output = True,
            text           = True,
            timeout        = 60,
            cwd            = '/home/hassan007/cybernews',
        )

        if result.returncode == 0:
            # Count how many articles are now in DB
            count = Article.query.filter_by(published=True).count()
            flash(
                f'✅ News fetched successfully! '
                f'Database now has {count} articles.',
                'success'
            )
        else:
            flash(
                f'⚠️ Fetch completed with warnings. Check rss_fetch.log',
                'warning'
            )

    except subprocess.TimeoutExpired:
        flash('⏱️ Fetch timed out. It may still be running.', 'warning')
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard'))

# ─────────────────────────────────────────
# VISITOR ANALYTICS DASHBOARD
# ─────────────────────────────────────────
@admin_bp.route('/analytics')
@login_required
def analytics():
    """Detailed visitor analytics dashboard."""
    from models import PageView, Article
    from sqlalchemy import func, distinct
    from datetime import datetime, timedelta
    from collections import Counter
    from urllib.parse import urlparse

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    active_since = now - timedelta(minutes=15)

    # Overview stats
    total_views = PageView.query.count()
    unique_visitors = db.session.query(
        func.count(distinct(PageView.ip_address))
    ).scalar() or 0

    today_views = PageView.query.filter(PageView.timestamp >= today).count()
    today_unique = db.session.query(
        func.count(distinct(PageView.ip_address))
    ).filter(PageView.timestamp >= today).scalar() or 0

    active_now = db.session.query(
        func.count(distinct(PageView.ip_address))
    ).filter(PageView.timestamp >= active_since).scalar() or 0

    week_views = PageView.query.filter(PageView.timestamp >= week_ago).count()
    month_views = PageView.query.filter(PageView.timestamp >= month_ago).count()

    # Repeat visitors (IPs with more than 1 visit)
    repeat_visitors = db.session.query(
        PageView.ip_address
    ).group_by(PageView.ip_address).having(
        func.count(PageView.id) > 1
    ).count()

    # Article page views
    article_views = PageView.query.filter(
        PageView.page.like('/article/%')
    ).count()

    stats = {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'today_views': today_views,
        'today_unique': today_unique,
        'active_now': active_now,
        'week_views': week_views,
        'month_views': month_views,
        'repeat_visitors': repeat_visitors,
        'article_views': article_views,
    }

    # Daily views last 7 days
    daily_views = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = PageView.query.filter(
            PageView.timestamp >= day_start,
            PageView.timestamp < day_end
        ).count()
        daily_views.append({
            'day': day_start.strftime('%a %d'),
            'count': count,
        })

    max_daily = max((d['count'] for d in daily_views), default=1) or 1

    # Hourly views today
    hourly = []
    for h in range(24):
        hour_start = today + timedelta(hours=h)
        hour_end = hour_start + timedelta(hours=1)
        count = PageView.query.filter(
            PageView.timestamp >= hour_start,
            PageView.timestamp < hour_end
        ).count()
        hourly.append({
            'hour': f'{h:02d}:00',
            'count': count,
        })

    max_hourly = max((h['count'] for h in hourly), default=1) or 1

    # Top pages
    top_pages = db.session.query(
        PageView.page,
        func.count(PageView.id).label('views')
    ).group_by(PageView.page).order_by(
        func.count(PageView.id).desc()
    ).limit(10).all()

    # Top article pages
    article_page_counts = db.session.query(
        PageView.page,
        func.count(PageView.id).label('views')
    ).filter(
        PageView.page.like('/article/%')
    ).group_by(PageView.page).order_by(
        func.count(PageView.id).desc()
    ).limit(10).all()

    top_articles = []
    for row in article_page_counts:
        try:
            article_id = int(row.page.strip('/').split('/')[-1])
            article = Article.query.get(article_id)
            if article:
                top_articles.append({
                    'id': article.id,
                    'title': article.title,
                    'views': row.views,
                    'source': article.source,
                })
        except Exception:
            pass

    # Devices
    devices = db.session.query(
        PageView.device,
        func.count(PageView.id).label('count')
    ).filter(PageView.device != None).group_by(
        PageView.device
    ).order_by(func.count(PageView.id).desc()).all()

    total_device = sum(d.count for d in devices) or 1

    # Browsers
    browsers = db.session.query(
        PageView.browser,
        func.count(PageView.id).label('count')
    ).filter(PageView.browser != None).group_by(
        PageView.browser
    ).order_by(func.count(PageView.id).desc()).all()

    total_browser = sum(b.count for b in browsers) or 1

    # Referrer domains
    ref_rows = PageView.query.filter(
        PageView.referrer != None,
        PageView.referrer != ''
    ).all()

    ref_counter = Counter()
    for row in ref_rows:
        try:
            domain = urlparse(row.referrer).netloc.lower().replace('www.', '')
            if domain:
                ref_counter[domain] += 1
        except Exception:
            pass

    top_referrers = ref_counter.most_common(10)

    # Recent visitors
    recent_visitors = PageView.query.order_by(
        PageView.timestamp.desc()
    ).limit(20).all()

    # Top visitor IPs
    top_ips = db.session.query(
        PageView.ip_address,
        func.count(PageView.id).label('views'),
        func.max(PageView.timestamp).label('last_visit')
    ).group_by(PageView.ip_address).order_by(
        func.count(PageView.id).desc()
    ).limit(15).all()

    return render_template(
        'admin/analytics.html',
        stats=stats,
        daily_views=daily_views,
        max_daily=max_daily,
        hourly=hourly,
        max_hourly=max_hourly,
        top_pages=top_pages,
        top_articles=top_articles,
        devices=devices,
        total_device=total_device,
        browsers=browsers,
        total_browser=total_browser,
        top_referrers=top_referrers,
        recent_visitors=recent_visitors,
        top_ips=top_ips,
    )

@admin_bp.route('/analytics/export.csv')
@login_required
def analytics_export():
    """Export recent analytics data as CSV."""
    from models import PageView
    from flask import Response
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'timestamp',
        'page',
        'ip_address',
        'device',
        'browser',
        'referrer',
        'user_agent',
    ])

    rows = PageView.query.order_by(
        PageView.timestamp.desc()
    ).limit(5000).all()

    for row in rows:
        writer.writerow([
            row.timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.timestamp else '',
            row.page or '',
            row.ip_address or '',
            row.device or '',
            row.browser or '',
            row.referrer or '',
            row.user_agent or '',
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=cybernews_analytics.csv'
        }
    )
