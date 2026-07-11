from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    abort,
    current_app,
    redirect,
    url_for,
    Response,
    send_from_directory,
)
from models import db, Article, Newsletter, PageView, LoginLog
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


def get_client_ip():
    """Get client IP safely."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


@main_bp.route('/')
def home():
    """Homepage with pagination and dynamic stats."""

    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Featured article
    featured = Article.query.filter_by(
        featured=True,
        published=True
    ).first()

    if not featured:
        today = datetime.utcnow().timetuple().tm_yday
        top_articles = Article.query.filter_by(
            published=True
        ).order_by(Article.created_at.desc()).limit(10).all()

        if top_articles:
            featured = top_articles[today % len(top_articles)]
        else:
            featured = None

    # Regular articles query
    query = Article.query.filter(Article.published == True)

    if featured:
        query = query.filter(Article.id != featured.id)

    # Mix sources while keeping newest days first
    query = query.order_by(
        db.func.date(Article.created_at).desc(),
        db.func.random()
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    if page > 1 and not pagination.items:
        return redirect(url_for('main.home'))

    # Latest articles for ticker/trending
    all_articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).limit(10).all()

    # Stats
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    stats = {
        'today': Article.query.filter(
            Article.published == True,
            Article.created_at >= today_start
        ).count(),
        'this_month': Article.query.filter(
            Article.published == True,
            Article.created_at >= month_start
        ).count(),
        'categories': len(current_app.config['CATEGORIES']),
        'total': Article.query.filter_by(published=True).count(),
    }

    # Threat level
    last_24h = now - timedelta(hours=24)

    threat_articles = Article.query.filter(
        Article.published == True,
        Article.created_at >= last_24h,
        Article.category.in_(['Malware', 'Threats', 'Vulnerabilities'])
    ).count()

    if threat_articles >= 16:
        threat_level = 'CRITICAL'
        threat_pct = min(95, 70 + threat_articles)
        threat_desc = f'{threat_articles} threat-related articles in the last 24 hours. Elevated activity detected.'
    elif threat_articles >= 6:
        threat_level = 'HIGH'
        threat_pct = min(70, 40 + threat_articles * 2)
        threat_desc = f'{threat_articles} threat-related articles detected in the last 24 hours.'
    elif threat_articles >= 1:
        threat_level = 'MEDIUM'
        threat_pct = min(45, 20 + threat_articles * 5)
        threat_desc = f'{threat_articles} threat-related articles in the last 24 hours. Stay vigilant.'
    else:
        threat_level = 'LOW'
        threat_pct = 15
        threat_desc = 'No significant threat activity detected in the last 24 hours.'

    threat_data = {
        'level': threat_level,
        'pct': threat_pct,
        'desc': threat_desc,
        'count': threat_articles,
    }

    return render_template(
        'index.html',
        featured=featured,
        regular=pagination.items,
        articles=all_articles,
        pagination=pagination,
        total_count=pagination.total,
        stats=stats,
        threat_data=threat_data,
    )


@main_bp.route('/article/<int:article_id>')
def article(article_id):
    """Show a single article."""
    post = db.get_or_404(Article, article_id)

    if not post.published:
        abort(404)

    related = Article.query.filter(
        Article.category == post.category,
        Article.id != post.id,
        Article.published == True,
    ).order_by(Article.created_at.desc()).limit(3).all()

    return render_template(
        'article.html',
        article=post,
        related=related,
    )


@main_bp.route('/categories')
def categories():
    """Show all categories with live counts."""
    cat_list = current_app.config['CATEGORIES']
    cat_data = []

    for cat_name in cat_list:
        count = Article.query.filter_by(
            category=cat_name,
            published=True,
        ).count()

        cat_data.append({
            'name': cat_name,
            'count': count,
        })

    return render_template(
        'categories.html',
        cat_data=cat_data,
    )


@main_bp.route('/category/<category_name>')
def category_detail(category_name):
    """Show one category with pagination."""
    valid_categories = current_app.config['CATEGORIES']
    if category_name not in valid_categories:
        abort(404)

    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = Article.query.filter_by(
        category=category_name,
        published=True,
    ).order_by(
        Article.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template(
        'category_detail.html',
        articles=pagination.items,
        pagination=pagination,
        category_name=category_name,
    )


@main_bp.route('/about')
def about():
    """About page."""
    stats = {
        'total_articles': Article.query.filter_by(published=True).count(),
        'categories': len(current_app.config['CATEGORIES']),
    }
    return render_template('about.html', stats=stats)


@main_bp.route('/robots.txt')
def robots():
    """Serve robots.txt."""
    return send_from_directory('static', 'robots.txt')


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate a dynamic sitemap."""
    articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).all()

    host = request.host_url.rstrip('/')

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for path in ['/', '/categories', '/about']:
        xml.append(f'''  <url>
    <loc>{host}{path}</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>''')

    for article in articles:
        xml.append(f'''  <url>
    <loc>{host}/article/{article.id}</loc>
    <lastmod>{article.created_at.strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>''')

    xml.append('</urlset>')

    return Response('\n'.join(xml), mimetype='application/xml')


@main_bp.route('/api/search')
def api_search():
    """Search published articles."""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'results': [], 'count': 0, 'query': ''})

    search_term = f'%{query}%'
    results = Article.query.filter(
        Article.published == True
    ).filter(
        db.or_(
            Article.title.ilike(search_term),
            Article.summary.ilike(search_term),
            Article.category.ilike(search_term),
            Article.source.ilike(search_term),
            Article.tags_string.ilike(search_term),
            Article.body.ilike(search_term),
        )
    ).order_by(Article.created_at.desc()).limit(50).all()

    return jsonify({
        'results': [a.to_dict() for a in results],
        'count': len(results),
        'query': query,
    })


@main_bp.route('/api/articles')
def api_articles():
    """Return all published articles as JSON."""
    category = request.args.get('category', '').strip()
    query = Article.query.filter_by(published=True)

    if category:
        query = query.filter_by(category=category)

    articles = query.order_by(Article.created_at.desc()).all()

    return jsonify({
        'articles': [a.to_dict() for a in articles],
        'count': len(articles),
    })


@main_bp.route('/api/stats')
def api_stats():
    """Return basic site statistics as JSON."""
    total = Article.query.filter_by(published=True).count()
    cats = Article.query.with_entities(Article.category).distinct().count()

    return jsonify({
        'total_articles': total,
        'total_categories': cats,
    })


@main_bp.route('/api/live-feed')
def api_live_feed():
    """Return real activity for the live monitor widget."""
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)

    events = []

    # Recent page views
    recent_views = PageView.query.filter(
        PageView.timestamp >= last_hour
    ).order_by(PageView.timestamp.desc()).limit(5).all()

    for view in recent_views:
        events.append({
            'type': 'info',
            'text': f'Page view: {view.page} from {view.ip_address}',
            'time': view.timestamp.strftime('%H:%M:%S'),
        })

    # Recent login attempts
    recent_logins = LoginLog.query.filter(
        LoginLog.timestamp >= last_24h
    ).order_by(LoginLog.timestamp.desc()).limit(3).all()

    for log in recent_logins:
        status = 'Login successful' if log.success else 'Login FAILED'
        log_type = 'success' if log.success else 'warn'
        events.append({
            'type': log_type,
            'text': f'{status}: {log.username} from {log.ip_address}',
            'time': log.timestamp.strftime('%H:%M:%S'),
        })

    # Article stats
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_articles = Article.query.filter(
        Article.published == True,
        Article.created_at >= today_start
    ).count()

    total_articles = Article.query.filter_by(published=True).count()

    events.append({
        'type': 'info',
        'text': f'Database: {total_articles} articles | {today_articles} new today',
        'time': now.strftime('%H:%M:%S'),
    })

    # Today's visitors
    today_views = PageView.query.filter(
        PageView.timestamp >= today_start
    ).count()

    unique_today = db.session.query(
        db.func.count(db.distinct(PageView.ip_address))
    ).filter(PageView.timestamp >= today_start).scalar() or 0

    events.append({
        'type': 'success',
        'text': f'Today: {today_views} views from {unique_today} unique visitors',
        'time': now.strftime('%H:%M:%S'),
    })

    # Recent subscribers
    recent_subs = Newsletter.query.filter(
        Newsletter.created_at >= last_24h
    ).order_by(Newsletter.created_at.desc()).limit(2).all()

    for sub in recent_subs:
        email = sub.email
        at_pos = email.find('@')
        if at_pos > 2:
            masked = email[:2] + '***' + email[at_pos:]
        else:
            masked = '***' + email[at_pos:]

        events.append({
            'type': 'success',
            'text': f'New subscriber: {masked}',
            'time': sub.created_at.strftime('%H:%M:%S'),
        })

    events.append({
        'type': 'success',
        'text': 'All systems operational. Security monitoring active.',
        'time': now.strftime('%H:%M:%S'),
    })

    return jsonify({
        'events': events,
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@main_bp.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    """Newsletter subscription API."""
    data = request.get_json(silent=True) or {}

    if data.get('website'):
        return jsonify({
            'success': True,
            'message': 'Subscribed successfully!'
        })

    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email address.',
        }), 400

    existing = Newsletter.query.filter_by(email=email).first()

    if existing:
        if existing.active:
            return jsonify({
                'success': False,
                'message': 'This email is already subscribed!',
            }), 400
        else:
            existing.active = True
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Welcome back! Subscription reactivated.',
            })

    subscription = Newsletter(email=email)
    db.session.add(subscription)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Subscribed successfully! Welcome to CyberNews.',
    })


@main_bp.route('/search')
def search_page():
    """Dedicated search results page."""
    query = request.args.get('q', '').strip()

    if not query:
        return render_template(
            'search.html',
            query='',
            results=[],
            count=0,
        )

    search_term = f'%{query}%'
    results = Article.query.filter(
        Article.published == True
    ).filter(
        db.or_(
            Article.title.ilike(search_term),
            Article.summary.ilike(search_term),
            Article.category.ilike(search_term),
            Article.source.ilike(search_term),
            Article.tags_string.ilike(search_term),
            Article.body.ilike(search_term),
        )
    ).order_by(Article.created_at.desc()).limit(50).all()

    return render_template(
        'search.html',
        query=query,
        results=results,
        count=len(results),
    )
