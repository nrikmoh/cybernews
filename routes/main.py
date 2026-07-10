# routes/main.py
from flask import (
    Blueprint, render_template, request,
    jsonify, abort, current_app,
)
from models import db, Article, Category, PageView

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/stats')
def api_stats():
    """Return site statistics as JSON."""
    total    = Article.query.filter_by(published=True).count()
    cats     = Article.query.with_entities(Article.category).distinct().count()

    return jsonify({
        'total_articles':  total,
        'total_categories': cats,
    })

# ─────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────
@main_bp.route('/')
def home():
    """Homepage with pagination."""
    from security import get_client_ip

    # Track page view
    try:
        PageView.record_view('/', get_client_ip())
    except Exception:
        pass

    # ── Pagination ─────────────────────────────────────
    # Get the current page number from URL: /?page=2
    # Default to page 1 if not specified
    page     = request.args.get('page', 1, type=int)
    per_page = 20  # articles per page

    # ── Featured Article ───────────────────────────────
    # First check for manually featured article
    featured = Article.query.filter_by(
        featured  = True,
        published = True,
    ).first()

    # If no manual feature, rotate daily
    # Pick a different top article each day automatically
    if not featured:
        from datetime import datetime
        today = datetime.utcnow().timetuple().tm_yday  # day of year (1-365)
        top_articles = Article.query.filter_by(
            published=True
        ).order_by(Article.created_at.desc()).limit(10).all()

        if top_articles:
            featured = top_articles[today % len(top_articles)]

    # Build query for regular articles (not featured)
    query = Article.query.filter(
        Article.published == True,
    )
    if featured:
        query = query.filter(Article.id != featured.id)

    # ── Order articles to mix sources ──────────────────
    # Instead of pure newest-first (which groups sources
    # together), we use a combination approach:
    # Sort by date (day level) then randomize within each day
    # This mixes sources while keeping recent articles on top
    query = query.order_by(
        db.func.date(Article.created_at).desc(),  # group by day
        db.func.random(),                         # shuffle within day
    )
    # ── Get paginated results ──────────────────────────
    # paginate() returns a Pagination object with:
    #   .items       → list of articles for THIS page
    #   .page        → current page number
    #   .pages       → total number of pages
    #   .total       → total number of articles
    #   .has_prev    → True if there's a previous page
    #   .has_next    → True if there's a next page
    #   .prev_num    → previous page number
    #   .next_num    → next page number
    pagination = query.paginate(
        page     = page,
        per_page = per_page,
        error_out = False,  # don't throw 404 for invalid pages
    )

    # If page is out of range, redirect to page 1
    if page > 1 and not pagination.items:
        return redirect(url_for('main.home'))

    # Trending articles for sidebar
    all_articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).limit(5).all()

    # ── Real Stats ─────────────────────────────────────
    from datetime import datetime, timedelta

    now   = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    stats = {
        'today':      Article.query.filter(
                          Article.published == True,
                          Article.created_at >= today,
                      ).count(),
        'this_month': Article.query.filter(
                          Article.published == True,
                          Article.created_at >= month_start,
                      ).count(),
        'categories': len(current_app.config['CATEGORIES']),
        'total':      Article.query.filter_by(published=True).count(),
    }

    # ── Threat Level Calculation ───────────────────────
    # Based on real articles in the last 24 hours
    last_24h = now - timedelta(hours=24)

    threat_articles = Article.query.filter(
        Article.published == True,
        Article.created_at >= last_24h,
        Article.category.in_(['Malware', 'Threats', 'Vulnerabilities']),
    ).count()

    # Calculate threat level: 0-5 = LOW, 6-15 = MEDIUM, 16+ = HIGH
    if threat_articles >= 16:
        threat_level = 'CRITICAL'
        threat_pct   = min(95, 70 + threat_articles)
        threat_desc  = f'{threat_articles} threat-related articles in the last 24 hours. Elevated activity detected.'
    elif threat_articles >= 6:
        threat_level = 'HIGH'
        threat_pct   = min(70, 40 + threat_articles * 2)
        threat_desc  = f'{threat_articles} threat-related articles detected in the last 24 hours.'
    elif threat_articles >= 1:
        threat_level = 'MEDIUM'
        threat_pct   = min(45, 20 + threat_articles * 5)
        threat_desc  = f'{threat_articles} threat-related articles in the last 24 hours. Stay vigilant.'
    else:
        threat_level = 'LOW'
        threat_pct   = 15
        threat_desc  = 'No significant threat activity detected in the last 24 hours.'

    threat_data = {
        'level':   threat_level,
        'pct':     threat_pct,
        'desc':    threat_desc,
        'count':   threat_articles,
    }

    return render_template(
        'index.html',
        featured    = featured,
        regular     = pagination.items,
        articles    = all_articles,
        pagination  = pagination,
        total_count = pagination.total,
        stats       = stats,
        threat_data = threat_data,
    )

# ─────────────────────────────────────────
# SINGLE ARTICLE PAGE
# ─────────────────────────────────────────
@main_bp.route('/article/<int:article_id>')
def article(article_id):
    """
    Show a single article.
    db.get_or_404() automatically returns 404 if not found.
    """

    # get_or_404 = get by primary key, or return 404 error
    post = db.get_or_404(Article, article_id)

    # Don't show unpublished articles to regular users
    if not post.published:
        abort(404)

    # Related articles: same category, not the same article
    related = Article.query.filter(
        Article.category  == post.category,
        Article.id        != post.id,
        Article.published == True,
    ).order_by(Article.created_at.desc()).limit(3).all()

    return render_template(
        'article.html',
        article = post,
        related = related,
    )


# ─────────────────────────────────────────
# CATEGORIES PAGE
# ─────────────────────────────────────────
@main_bp.route('/categories')
def categories():
    """
    Show all categories with article counts.
    We query the database for live counts.
    """

    # Build a dict: category_name → article count
    # We query each category separately for simplicity
    cat_list    = current_app.config['CATEGORIES']
    cat_data    = []

    for cat_name in cat_list:
        count = Article.query.filter_by(
            category  = cat_name,
            published = True,
        ).count()

        cat_data.append({
            'name':  cat_name,
            'count': count,
        })

    return render_template(
        'categories.html',
        cat_data = cat_data,
    )


# ─────────────────────────────────────────
# CATEGORY DETAIL PAGE
# ─────────────────────────────────────────
@main_bp.route('/category/<category_name>')
def category_detail(category_name):
    """Show all articles in a category with pagination."""

    valid_categories = current_app.config['CATEGORIES']
    if category_name not in valid_categories:
        abort(404)

    page     = request.args.get('page', 1, type=int)
    per_page = 9

    pagination = Article.query.filter_by(
        category  = category_name,
        published = True,
    ).order_by(
        Article.created_at.desc()
    ).paginate(
        page      = page,
        per_page  = per_page,
        error_out = False,
    )

    return render_template(
        'category_detail.html',
        articles      = pagination.items,
        pagination    = pagination,
        category_name = category_name,
    )

# ─────────────────────────────────────────
# ABOUT PAGE
# ─────────────────────────────────────────
@main_bp.route('/about')
def about():
    # Pass some live stats to the about page
    stats = {
        'total_articles': Article.query.filter_by(published=True).count(),
        'categories':     len(current_app.config['CATEGORIES']),
    }
    return render_template('about.html', stats=stats)


# ─────────────────────────────────────────
# JSON API: SEARCH
# ─────────────────────────────────────────
@main_bp.route('/api/search')
def api_search():
    """
    Search articles using SQLAlchemy's ilike() for
    case-insensitive pattern matching.
    
    ilike('%query%') means:
      % = anything before
      query = the search term
      % = anything after
    So it matches any string CONTAINING the query.
    """
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'results': [], 'count': 0, 'query': ''})

    # Search in title, summary, category, and source
    # We use the | (or) operator to combine conditions
    search_term = f'%{query}%'   # wrap with % for SQL LIKE
    results = Article.query.filter(
        Article.published == True,
    ).filter(
        db.or_(
            Article.title.ilike(search_term),
            Article.summary.ilike(search_term),
            Article.category.ilike(search_term),
            Article.source.ilike(search_term),
            Article.tags_string.ilike(search_term),
        )
    ).order_by(Article.created_at.desc()).all()

    return jsonify({
        'results': [a.to_dict() for a in results],
        'count':   len(results),
        'query':   query,
    })


# ─────────────────────────────────────────
# JSON API: ALL ARTICLES
# ─────────────────────────────────────────
@main_bp.route('/api/articles')
def api_articles():
    """Return all published articles as JSON."""

    category = request.args.get('category', '').strip()
    query    = Article.query.filter_by(published=True)

    if category:
        query = query.filter_by(category=category)

    articles = query.order_by(Article.created_at.desc()).all()

    return jsonify({
        'articles': [a.to_dict() for a in articles],
        'count':    len(articles),
    })


# ─────────────────────────────────────────
# JSON API: NEWSLETTER SUBSCRIBE
# ─────────────────────────────────────────
@main_bp.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    """
    Handle newsletter subscriptions.
    Accepts POST request with JSON body: {"email": "user@example.com"}
    """
    from models import Newsletter

    data  = request.get_json()
    # Honeypot check — if 'website' field has data, it's a bot
    if data and data.get('website'):
        # Silently reject — don't tell the bot we caught it
        return jsonify({
            'success': True,
            'message': 'Subscribed successfully!',
        })

    email = data.get('email', '').strip().lower() if data else ''

    if not email or '@' not in email:
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email address.',
        }), 400

    # Check if already subscribed
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        if existing.active:
            return jsonify({
                'success': False,
                'message': 'This email is already subscribed!',
            }), 400
        else:
            # Re-activate cancelled subscription
            existing.active = True
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Welcome back! Subscription reactivated.',
            })

    # Create new subscription
    subscription = Newsletter(email=email)
    db.session.add(subscription)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Subscribed successfully! Welcome to CyberNews.',
    })
