# routes/main.py
# ─────────────────────────────────────────────────────────
# Main routes for CyberNews:
#   /              → homepage
#   /article/<id>  → single article page
#   /categories    → categories overview
#   /about         → about page
#   /search        → search results (API endpoint)
# ─────────────────────────────────────────────────────────

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    abort,
    current_app,
)
from data import (
    get_all_articles,
    get_featured_article,
    get_regular_articles,
    get_article_by_id,
    get_articles_by_category,
    get_related_articles,
    search_articles,
    get_category_counts,
)

# Create the blueprint
# 'main' is the name — used when referring to routes with url_for()
main_bp = Blueprint('main', __name__)


# ─────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────
@main_bp.route('/')
def home():
    """
    The main homepage showing featured story and article grid.
    We pass all the data the template needs as keyword arguments.
    """
    featured = get_featured_article()
    regular  = get_regular_articles()
    articles = get_all_articles()

    return render_template(
        'index.html',
        featured  = featured,
        regular   = regular,
        articles  = articles,
        page_title = 'Latest Cybersecurity News',
    )


# ─────────────────────────────────────────
# SINGLE ARTICLE PAGE
# ─────────────────────────────────────────
@main_bp.route('/article/<int:article_id>')
def article(article_id):
    """
    Display a single article.
    <int:article_id> tells Flask to capture the number from the URL
    and convert it to a Python integer automatically.
    """
    post = get_article_by_id(article_id)

    # If article not found, return 404 error
    if post is None:
        abort(404)

    # Get related articles for the sidebar
    related = get_related_articles(article_id, count=3)

    return render_template(
        'article.html',
        article   = post,
        related   = related,
        page_title = post['title'],
    )


# ─────────────────────────────────────────
# CATEGORIES PAGE
# ─────────────────────────────────────────
@main_bp.route('/categories')
def categories():
    """
    Show all categories with article counts.
    """
    counts = get_category_counts()

    return render_template(
        'categories.html',
        category_counts = counts,
        page_title      = 'Browse Categories',
    )


# ─────────────────────────────────────────
# CATEGORY DETAIL PAGE
# ─────────────────────────────────────────
@main_bp.route('/category/<category_name>')
def category_detail(category_name):
    """
    Show all articles in a specific category.
    <category_name> is captured from the URL as a string.
    """
    # Get articles for this category
    cat_articles = get_articles_by_category(category_name)

    # If no articles found for this category, return 404
    if not cat_articles and category_name not in current_app.config['CATEGORIES']:
        abort(404)

    return render_template(
        'category_detail.html',
        articles      = cat_articles,
        category_name = category_name,
        page_title    = f'{category_name} News',
    )


# ─────────────────────────────────────────
# SEARCH — JSON API ENDPOINT
# ─────────────────────────────────────────
@main_bp.route('/api/search')
def api_search():
    """
    Search endpoint that returns JSON results.
    JavaScript can call this to get search results without
    reloading the page (AJAX request).
    
    Usage: GET /api/search?q=ransomware
    Returns: JSON array of matching articles
    """
    # Get the search query from URL parameters
    # e.g. /api/search?q=ransomware → query = 'ransomware'
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({
            'results': [],
            'count':   0,
            'query':   '',
        })

    results = search_articles(query)

    # We can't send Python dicts with all fields directly
    # (some might not be JSON-serializable later with DB objects)
    # So we explicitly select what to send
    serialized = [
        {
            'id':       a['id'],
            'title':    a['title'],
            'summary':  a['summary'],
            'category': a['category'],
            'source':   a['source'],
            'date':     a['date'],
            'image':    a['image'],
            'url':      f"/article/{a['id']}",
        }
        for a in results
    ]

    return jsonify({
        'results': serialized,
        'count':   len(serialized),
        'query':   query,
    })


# ─────────────────────────────────────────
# API — ALL ARTICLES (JSON)
# ─────────────────────────────────────────
@main_bp.route('/api/articles')
def api_articles():
    """
    Returns all articles as JSON.
    Useful for future features (mobile app, external integrations).
    
    Optional filter: GET /api/articles?category=Malware
    """
    category = request.args.get('category', '').strip()

    if category:
        articles = get_articles_by_category(category)
    else:
        articles = get_all_articles()

    serialized = [
        {
            'id':       a['id'],
            'title':    a['title'],
            'summary':  a['summary'],
            'category': a['category'],
            'source':   a['source'],
            'date':     a['date'],
            'url':      f"/article/{a['id']}",
        }
        for a in articles
    ]

    return jsonify({
        'articles': serialized,
        'count':    len(serialized),
    })


# ─────────────────────────────────────────
# ABOUT PAGE
# ─────────────────────────────────────────
@main_bp.route('/about')
def about():
    return render_template(
        'about.html',
        page_title = 'About CyberNews',
    )
