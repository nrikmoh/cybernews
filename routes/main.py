# routes/main.py
from flask import (
    Blueprint, render_template, request,
    jsonify, abort, current_app,
)
from models import db, Article, Category

main_bp = Blueprint('main', __name__)


# ─────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────
@main_bp.route('/')
def home():
    """
    Homepage: featured article + article grid.
    We query the database instead of the old Python list.
    """

    # Get featured article (first one marked as featured)
    featured = Article.query.filter_by(
        featured  = True,
        published = True,
    ).first()

    # If no featured article exists, use the most recent one
    if not featured:
        featured = Article.query.filter_by(
            published=True
        ).order_by(Article.created_at.desc()).first()

    # Get all other published articles (not the featured one)
    # ordered by newest first
    if featured:
        regular = Article.query.filter(
            Article.published == True,
            Article.id        != featured.id,
        ).order_by(Article.created_at.desc()).all()
    else:
        regular = []

    # All articles for the sidebar trending list
    all_articles = Article.query.filter_by(
        published=True
    ).order_by(Article.created_at.desc()).limit(5).all()

    return render_template(
        'index.html',
        featured     = featured,
        regular      = regular,
        articles     = all_articles,
        total_count  = Article.query.filter_by(published=True).count(),
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
    """Show all articles in a specific category."""

    valid_categories = current_app.config['CATEGORIES']
    if category_name not in valid_categories:
        abort(404)

    cat_articles = Article.query.filter_by(
        category  = category_name,
        published = True,
    ).order_by(Article.created_at.desc()).all()

    return render_template(
        'category_detail.html',
        articles      = cat_articles,
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
