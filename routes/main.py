from flask import (
    Blueprint, render_template, request,
    jsonify, abort, current_app,
    redirect, url_for, Response,
    send_from_directory,
)
from models import db, Article, Newsletter, PageView, LoginLog
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


@main_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    featured = Article.query.filter_by(
        featured=True, published=True
    ).first()

    if not featured:
        today = datetime.utcnow().timetuple().tm_yday
        top = Article.query.filter_by(
            published=True
        ).order_by(Article.created_at.desc()).limit(10).all()
        if top:
            featured = top[today % len(top)]

    query = Article.query.filter(Article.published == True)
    if featured:
        query = query.filter(Article.id != featured.id)

    query = query.order_by(
        db.func.date(Article.created_at).desc(),
        db.func.random()
    )

    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    if page > 1 and not pagination.items:
        return redirect(url_for('main.home'))

    all_articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).limit(10).all()

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

    last_24h = now - timedelta(hours=24)
    threat_count = Article.query.filter(
        Article.published == True,
        Article.created_at >= last_24h,
        Article.category.in_(['Malware', 'Threats', 'Vulnerabilities'])
    ).count()

    if threat_count >= 16:
        tl, tp = 'CRITICAL', min(95, 70 + threat_count)
        td = f'{threat_count} threat articles in 24h. Elevated activity.'
    elif threat_count >= 6:
        tl, tp = 'HIGH', min(70, 40 + threat_count * 2)
        td = f'{threat_count} threat articles in 24h.'
    elif threat_count >= 1:
        tl, tp = 'MEDIUM', min(45, 20 + threat_count * 5)
        td = f'{threat_count} threat articles in 24h. Stay vigilant.'
    else:
        tl, tp = 'LOW', 15
        td = 'No significant threats in 24h.'

    threat_data = {'level': tl, 'pct': tp, 'desc': td, 'count': threat_count}

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
    post = db.get_or_404(Article, article_id)
    if not post.published:
        abort(404)
    related = Article.query.filter(
        Article.category == post.category,
        Article.id != post.id,
        Article.published == True,
    ).order_by(Article.created_at.desc()).limit(3).all()
    return render_template('article.html', article=post, related=related)


@main_bp.route('/categories')
def categories():
    cat_data = []
    for cat_name in current_app.config['CATEGORIES']:
        count = Article.query.filter_by(
            category=cat_name, published=True
        ).count()
        cat_data.append({'name': cat_name, 'count': count})
    return render_template('categories.html', cat_data=cat_data)


@main_bp.route('/category/<category_name>')
def category_detail(category_name):
    if category_name not in current_app.config['CATEGORIES']:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter_by(
        category=category_name, published=True
    ).order_by(
        Article.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template(
        'category_detail.html',
        articles=pagination.items,
        pagination=pagination,
        category_name=category_name,
    )


@main_bp.route('/about')
def about():
    stats = {
        'total_articles': Article.query.filter_by(published=True).count(),
        'categories': len(current_app.config['CATEGORIES']),
    }
    return render_template('about.html', stats=stats)


@main_bp.route('/search')
def search_page():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search.html', query='', results=[], count=0)
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
        'search.html', query=query, results=results, count=len(results)
    )


@main_bp.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


@main_bp.route('/sitemap.xml')
def sitemap():
    articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).all()
    host = request.host_url.rstrip('/')
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for path in ['/', '/categories', '/about']:
        xml.append(f'  <url><loc>{host}{path}</loc><changefreq>daily</changefreq></url>')
    for a in articles:
        xml.append(f'  <url><loc>{host}/article/{a.id}</loc><lastmod>{a.created_at.strftime("%Y-%m-%d")}</lastmod></url>')
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype='application/xml')


@main_bp.route('/api/search')
def api_search():
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
    total = Article.query.filter_by(published=True).count()
    cats = Article.query.with_entities(Article.category).distinct().count()
    return jsonify({'total_articles': total, 'total_categories': cats})


@main_bp.route('/api/live-feed')
def api_live_feed():
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = []

    views = PageView.query.filter(
        PageView.timestamp >= last_hour
    ).order_by(PageView.timestamp.desc()).limit(5).all()
    for v in views:
        events.append({
            'type': 'info',
            'text': f'Page view: {v.page} from {v.ip_address}',
            'time': v.timestamp.strftime('%H:%M:%S'),
        })

    logins = LoginLog.query.filter(
        LoginLog.timestamp >= last_24h
    ).order_by(LoginLog.timestamp.desc()).limit(3).all()
    for log in logins:
        status = 'Login OK' if log.success else 'Login FAILED'
        events.append({
            'type': 'success' if log.success else 'warn',
            'text': f'{status}: {log.username} from {log.ip_address}',
            'time': log.timestamp.strftime('%H:%M:%S'),
        })

    total = Article.query.filter_by(published=True).count()
    today_new = Article.query.filter(
        Article.published == True,
        Article.created_at >= today_start
    ).count()
    events.append({
        'type': 'info',
        'text': f'Database: {total} articles | {today_new} new today',
        'time': now.strftime('%H:%M:%S'),
    })

    today_views = PageView.query.filter(
        PageView.timestamp >= today_start
    ).count()
    unique = db.session.query(
        db.func.count(db.distinct(PageView.ip_address))
    ).filter(PageView.timestamp >= today_start).scalar() or 0
    events.append({
        'type': 'success',
        'text': f'Today: {today_views} views from {unique} visitors',
        'time': now.strftime('%H:%M:%S'),
    })

    events.append({
        'type': 'success',
        'text': 'All systems operational.',
        'time': now.strftime('%H:%M:%S'),
    })

    return jsonify({
        'events': events,
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@main_bp.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    data = request.get_json(silent=True) or {}
    if data.get('website'):
        return jsonify({'success': True, 'message': 'OK'})
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Invalid email.'}), 400
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        if existing.active:
            return jsonify({'success': False, 'message': 'Already subscribed.'}), 400
        existing.active = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reactivated.'})
    sub = Newsletter(email=email)
    db.session.add(sub)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Subscribed!'})
