from flask import (
    Blueprint, render_template, request,
    jsonify, abort, current_app,
    redirect, url_for, Response,
    send_from_directory,
)
from models import db, Article, Newsletter, PageView, LoginLog, ContactMessage
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
    """Return real activity including attack data for the live monitor."""
    import os
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = []

    # ── Recent page views ──────────────────────────────
    views = PageView.query.filter(
        PageView.timestamp >= last_hour
    ).order_by(PageView.timestamp.desc()).limit(3).all()

    for v in views:
        # Mask last IP octet for privacy
        ip = v.ip_address or 'unknown'
        if '.' in ip:
            parts = ip.split('.')
            ip = f'{parts[0]}.{parts[1]}.{parts[2]}.xxx'

        events.append({
            'type': 'info',
            'text': f'Visitor: {ip} → {v.page}',
            'time': v.timestamp.strftime('%H:%M:%S'),
        })

    # ── Recent login attempts ──────────────────────────
    logins = LoginLog.query.filter(
        LoginLog.timestamp >= last_24h
    ).order_by(LoginLog.timestamp.desc()).limit(5).all()

    for log in logins:
        ip = log.ip_address or 'unknown'
        if log.success:
            events.append({
                'type': 'success',
                'text': f'Admin login: {log.username} from {ip}',
                'time': log.timestamp.strftime('%H:%M:%S'),
            })
        else:
            events.append({
                'type': 'error',
                'text': f'FAILED login: {log.username} from {ip}',
                'time': log.timestamp.strftime('%H:%M:%S'),
            })

    # ── Blocked attacks from security.log ──────────────
    try:
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'security.log'
        )
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()

            # Get last 50 blocked entries
            blocked = [l.strip() for l in lines if 'BLOCKED' in l]
            recent_blocks = blocked[-10:]

            for line in recent_blocks:
                parts = line.split(' | ')
                reason = ''
                ip = ''
                path = ''
                ua = ''
                timestamp = ''

                for part in parts:
                    part = part.strip()
                    if part.startswith('20'):
                        timestamp = part[-8:]
                    if 'Reason:' in part:
                        reason = part.replace('Reason: ', '').strip()
                    if 'IP:' in part:
                        ip = part.replace('IP: ', '').strip()
                    if 'Path:' in part:
                        path = part.replace('Path: ', '').strip()
                    if 'UA:' in part:
                        ua = part.replace('UA: ', '').strip()[:50]

                if reason:
                    events.append({
                        'type': 'error',
                        'text': f'BLOCKED {ip}: {reason} → {path}',
                        'time': timestamp or now.strftime('%H:%M:%S'),
                    })
    except Exception:
        pass

    # ── Blocked attacks from nginx log ─────────────────
    try:
        nginx_log = '/var/log/nginx/cybernews_access.log'
        if os.path.exists(nginx_log):
            with open(nginx_log, 'r') as f:
                lines = f.readlines()

            # Find recent 403 and 429 responses
            blocked_nginx = []
            for line in lines[-200:]:
                if '" 403 ' in line or '" 429 ' in line:
                    blocked_nginx.append(line.strip())

            for line in blocked_nginx[-5:]:
                try:
                    ip = line.split(' ')[0]
                    # Extract the requested path
                    request_part = line.split('"')[1] if '"' in line else ''
                    method_path = request_part.split(' ')
                    path = method_path[1] if len(method_path) > 1 else '/'

                    # Determine type
                    if '" 429 ' in line:
                        events.append({
                            'type': 'warn',
                            'text': f'Rate limited: {ip} → {path}',
                            'time': now.strftime('%H:%M:%S'),
                        })
                    else:
                        events.append({
                            'type': 'error',
                            'text': f'Nginx blocked: {ip} → {path}',
                            'time': now.strftime('%H:%M:%S'),
                        })
                except Exception:
                    pass
    except Exception:
        pass

    # ── Fail2ban banned IPs ────────────────────────────
    try:
        import subprocess
        result = subprocess.run(
            ['sudo', 'fail2ban-client', 'status'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # Count total bans
            jail_output = result.stdout
            if 'Number of jail' in jail_output:
                events.append({
                    'type': 'warn',
                    'text': f'Fail2ban: monitoring active',
                    'time': now.strftime('%H:%M:%S'),
                })
    except Exception:
        pass

    # ── System stats ───────────────────────────────────
    total_articles = Article.query.filter_by(published=True).count()
    today_articles = Article.query.filter(
        Article.published == True,
        Article.created_at >= today_start
    ).count()

    events.append({
        'type': 'info',
        'text': f'Database: {total_articles} articles | {today_articles} new today',
        'time': now.strftime('%H:%M:%S'),
    })

    # Today visitors
    today_views = PageView.query.filter(
        PageView.timestamp >= today_start
    ).count()
    unique = db.session.query(
        db.func.count(db.distinct(PageView.ip_address))
    ).filter(PageView.timestamp >= today_start).scalar() or 0

    events.append({
        'type': 'success',
        'text': f'Today: {today_views} views | {unique} unique visitors',
        'time': now.strftime('%H:%M:%S'),
    })

    # ── Attack summary ─────────────────────────────────
    try:
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'security.log'
        )
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()

            total_blocked = content.count('BLOCKED')
            total_failed_logins = content.count('LOGIN FAILED')

            events.append({
                'type': 'warn',
                'text': f'Total blocked: {total_blocked} attacks | {total_failed_logins} failed logins',
                'time': now.strftime('%H:%M:%S'),
            })
    except Exception:
        pass

    # System status
    events.append({
        'type': 'success',
        'text': 'All systems operational. Security monitoring active.',
        'time': now.strftime('%H:%M:%S'),
    })

    return jsonify({
        'events': events,
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    return render_template('terms.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with message form."""
    success = False
    error = None

    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Honeypot check
        if request.form.get('website', ''):
            # Bot detected — pretend success
            success = True
            return render_template('contact.html', success=True)

        # Validation
        if not name or len(name) < 2:
            error = 'Please enter your name.'
        elif not email or '@' not in email or '.' not in email:
            error = 'Please enter a valid email address.'
        elif not subject or len(subject) < 3:
            error = 'Please enter a subject.'
        elif not message or len(message) < 10:
            error = 'Message must be at least 10 characters.'
        elif len(message) > 5000:
            error = 'Message is too long (max 5000 characters).'
        else:
            try:
                # Save to database
                msg = ContactMessage(
                    name       = name[:100],
                    email      = email[:120],
                    subject    = subject[:200],
                    message    = message[:5000],
                    ip_address = get_client_ip(),
                )
                db.session.add(msg)
                db.session.commit()
                success = True
            except Exception:
                db.session.rollback()
                error = 'Something went wrong. Please try again.'

    return render_template(
        'contact.html',
        success=success,
        error=error,
    )

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

@main_bp.route('/.well-known/security.txt')
def security_txt():
    return send_from_directory(
        'static/.well-known',
        'security.txt',
        mimetype='text/plain'
    )
