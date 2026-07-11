# rss_fetcher.py
# ─────────────────────────────────────────────────────────
# Automatic RSS feed fetcher for CyberNews.
#
# This script:
# 1. Fetches real cybersecurity news from RSS feeds
# 2. Saves new articles to the database
# 3. Can run once manually OR on a schedule
#
# Usage:
#   python rss_fetcher.py          → fetch once now
#   python rss_fetcher.py --watch  → fetch every hour forever
# ─────────────────────────────────────────────────────────

import sys
import time
import hashlib
import logging
import feedparser
import requests
from datetime  import datetime
from app       import app
from models    import db, Article

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = '%(asctime)s | %(levelname)s | %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('rss_fetcher')

# ── Image Sources ──────────────────────────────────────
# Curated list of cybersecurity images from Unsplash
# organized by keyword/theme

CYBER_IMAGES = {
    'malware': [
        'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
    ],
    'ransomware': [
        'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80',
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
    ],
    'breach': [
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
    ],
    'vulnerability': [
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
    ],
    'privacy': [
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
        'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80',
    ],
    'hacking': [
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
    ],
    'phishing': [
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
    ],
    'encryption': [
        'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
    ],
    'government': [
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
    ],
    'network': [
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
    ],
    'cloud': [
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
    ],
    'ai': [
        'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
    ],
    'microsoft': [
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80',
    ],
    'google': [
        'https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
    ],
    'apple': [
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
    ],
    'linux': [
        'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
    ],
    'default': [
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80',
        'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
        'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80',
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80',
    ],
}

# ── Smart Image Generator ─────────────────────────────
# Uses article keywords to generate unique relevant images
# Each article gets a different image based on its title


def find_best_image(title, summary, default_image=None):
    """
    Return a LOCAL photo path with maximum variety.
    Uses ALL photos across all categories to minimize repetition.
    First tries category-specific, then falls back to any photo.
    """
    import hashlib
    import os

    text = (title + ' ' + summary).lower()

    # Determine primary category
    category = 'general'
    if any(k in text for k in ['ransomware', 'malware', 'trojan', 'virus', 'spyware', 'botnet', 'backdoor', 'rootkit']):
        category = 'malware'
    elif any(k in text for k in ['breach', 'leak', 'compromised', 'stolen', 'exposed', 'dump', 'records']):
        category = 'breaches'
    elif any(k in text for k in ['vulnerability', 'zero-day', 'cve-', 'exploit', 'patch', 'rce', 'flaw']):
        category = 'vulnerabilities'
    elif any(k in text for k in ['privacy', 'gdpr', 'tracking', 'surveillance', 'consent', 'regulation']):
        category = 'privacy'
    elif any(k in text for k in ['apt', 'threat', 'phishing', 'ddos', 'government', 'espionage', 'campaign']):
        category = 'threats'
    elif any(k in text for k in ['research', 'analysis', 'report', 'study', 'tool', 'framework', 'discovered']):
        category = 'research'

    # Build a MASTER list of all available photos
    base_dir = os.path.join('static', 'images', 'photos')
    all_photos = []

    # Category photos first (higher priority)
    cat_dir = os.path.join(base_dir, category)
    try:
        cat_photos = sorted([
            f'/static/images/photos/{category}/{f}'
            for f in os.listdir(cat_dir)
            if f.endswith('.jpg')
        ])
        all_photos.extend(cat_photos)
    except FileNotFoundError:
        pass

    # Then add ALL other category photos
    all_categories = ['malware', 'breaches', 'vulnerabilities',
                      'privacy', 'threats', 'research', 'general']
    for other_cat in all_categories:
        if other_cat == category:
            continue
        other_dir = os.path.join(base_dir, other_cat)
        try:
            other_photos = sorted([
                f'/static/images/photos/{other_cat}/{f}'
                for f in os.listdir(other_dir)
                if f.endswith('.jpg')
            ])
            all_photos.extend(other_photos)
        except FileNotFoundError:
            pass

    if not all_photos:
        return '/static/images/fallback/cyber-default.jpg'

    # Use a hash of the FULL title (not just keywords) to pick
    # This ensures maximum spread across the entire library
    h = int(hashlib.md5(title.encode()).hexdigest(), 16)
    return all_photos[h % len(all_photos)]


# ── Category Keywords ──────────────────────────────────
# These help us auto-detect the right category
# based on keywords in the article title

CATEGORY_KEYWORDS = {
    'Malware': [
        'malware', 'ransomware', 'trojan', 'virus', 'worm',
        'spyware', 'botnet', 'rootkit', 'backdoor', 'keylogger',
        'cryptominer', 'rat ', 'dropper',
    ],
    'Data Breaches': [
        'breach', 'leak', 'exposed', 'stolen', 'data breach',
        'records exposed', 'database leaked', 'hacked', 'compromised',
        'million records', 'billion records',
    ],
    'Vulnerabilities': [
        'vulnerability', 'cve-', 'zero-day', 'zero day', 'patch',
        'exploit', 'rce', 'remote code', 'sql injection', 'xss',
        'buffer overflow', 'critical flaw', 'security flaw', 'unpatched',
    ],
    'Privacy': [
        'privacy', 'gdpr', 'surveillance', 'tracking', 'data protection',
        'personal data', 'spy', 'spying', 'wiretap', 'facial recognition',
    ],
    'Research': [
        'research', 'discovered', 'analysis', 'report', 'study',
        'academic', 'paper', 'tool', 'framework', 'technique',
        'method', 'found', 'reveals',
    ],
    'Threats': [
        'apt', 'nation state', 'chinese hackers', 'russian hackers',
        'north korea', 'iran', 'threat actor', 'campaign', 'attack',
        'phishing', 'ddos', 'infrastructure', 'espionage',
    ],
}


def detect_category(title, summary, default_category):
    """
    Automatically detect the best category for an article
    by looking for keywords in the title and summary.
    
    Returns the detected category or the default one.
    """
    # Combine title and summary for keyword search
    text = (title + ' ' + summary).lower()

    # Score each category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    # Return the highest scoring category
    if scores:
        return max(scores, key=scores.get)

    return default_category


def make_article_id(title, source):
    """
    Create a unique fingerprint for an article
    based on its title and source.
    
    We use this to avoid adding duplicate articles.
    MD5 is fine here — we're not using it for security,
    just for deduplication.
    """
    unique_string = f"{title.lower().strip()}{source.lower()}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def article_exists(title, source):
    """
    Check if an article with this title already exists
    in the database.
    """
    # Simple check: does any article have this exact title?
    existing = Article.query.filter(
        Article.title   == title,
        Article.source  == source,
    ).first()
    return existing is not None


def clean_text(text):
    """
    Clean up text from RSS feeds.
    RSS feeds sometimes contain HTML tags or extra whitespace.
    """
    if not text:
        return ''

    import re

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Fix common HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;',  '<')
    text = text.replace('&gt;',  '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')

    return text.strip()


def fetch_feed(feed_config):
    """
    Fetch and parse one RSS feed.
    Returns a list of new articles that were added to the database.
    """
    url    = feed_config['url']
    source = feed_config['source']
    logger.info(f'Fetching: {source} ({url})')

    try:
        # feedparser handles the HTTP request and XML parsing
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            logger.warning(f'Failed to parse feed: {source}')
            return 0

        new_count = 0

        for entry in feed.entries:

            # ── Extract article data ───────────────────
            title   = clean_text(getattr(entry, 'title', ''))
            summary = clean_text(getattr(entry, 'summary', ''))

            # Skip if no title or too short
            if not title or len(title) < 10:
                continue

            # Skip if too short summary
            if len(summary) < 20:
                summary = f"Read the full article at {source} for complete details about this cybersecurity news story."

            # Truncate very long summaries
            if len(summary) > 500:
                summary = summary[:497] + '...'

            # ── Check for duplicates ───────────────────
            if article_exists(title, source):
                continue  # skip — already in database

            # ── Detect best category ───────────────────
            category = detect_category(
                title,
                summary,
                feed_config['category'],
            )

            # ── Get article image ──────────────────────
            image_url = None

            # Try to find an image in the RSS entry itself
            if hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if media.get('type', '').startswith('image'):
                        image_url = media.get('url')
                        break

            if not image_url and hasattr(entry, 'media_thumbnail'):
                for thumb in entry.media_thumbnail:
                    if thumb.get('url'):
                        image_url = thumb.get('url')
                        break

            if not image_url and hasattr(entry, 'links'):
                for link in entry.links:
                    if link.get('type', '').startswith('image'):
                        image_url = link.get('href')
                        break

            if not image_url and hasattr(entry, 'enclosures'):
                for enc in entry.enclosures:
                    if enc.get('type', '').startswith('image'):
                        image_url = enc.get('href')
                        break

            # ONLY use our image picker if NO image was found from feed
            if not image_url:
                image_url = find_best_image(
                    title,
                    summary,
                    feed_config['default_image']
                )

            # ── Build the article body ─────────────────
            # RSS feeds often only give us a summary.
            # We build a proper body from what we have.
            body = summary

            # If the entry has full content, use that
            if hasattr(entry, 'content'):
                for content in entry.content:
                    if content.get('type') == 'text/html':
                        body = clean_text(content.get('value', summary))
                        break

            # Add source link at the end
            article_link = getattr(entry, 'link', '')
            if article_link:
                body += f"\n\nRead the original article at {source}: {article_link}"

            # ── Extract tags ───────────────────────────
            tags = []
            if hasattr(entry, 'tags'):
                tags = [
                    clean_text(t.get('term', ''))
                    for t in entry.tags[:5]
                    if t.get('term')
                ]

            # Always add category as a tag
            if category not in tags:
                tags.insert(0, category)

            # ── Save to database ───────────────────────
            article = Article(
                title       = title[:300],
                summary     = summary[:500],
                body        = body,
                category    = category,
                source      = source,
                image_url   = image_url,
                featured    = False,
                published   = True,
                tags_string = ', '.join(tags[:5]),
            )

            db.session.add(article)
            new_count += 1

        # Commit all new articles from this feed at once
        if new_count > 0:
            db.session.commit()
            logger.info(f'  ✓ Added {new_count} new articles from {source}')
        else:
            logger.info(f'  → No new articles from {source}')

        return new_count

    except Exception as e:
        logger.error(f'Error fetching {source}: {e}')
        db.session.rollback()
        return 0


def fetch_all_feeds():
    """
    Fetch all configured RSS feeds.
    This is the main function that does everything.
    """
    logger.info('=' * 50)
    logger.info('Starting RSS fetch cycle')
    logger.info('=' * 50)

    total_new = 0

    with app.app_context():
        for feed_config in FEEDS:
            count     = fetch_feed(feed_config)
            total_new += count
            # Small delay between feeds to be polite to servers
            time.sleep(2)

    logger.info('=' * 50)
    logger.info(f'Fetch complete. Total new articles: {total_new}')
    logger.info('=' * 50)

    return total_new


def run_scheduler(interval_minutes=60):
    """
    Run the fetcher on a schedule.
    Fetches immediately, then repeats every interval_minutes.
    """
    logger.info(f'Starting RSS scheduler (every {interval_minutes} minutes)')

    while True:
        fetch_all_feeds()

        logger.info(f'Next fetch in {interval_minutes} minutes...')
        logger.info(f'Press Ctrl+C to stop')

        # Wait for the next cycle
        time.sleep(interval_minutes * 60)


# ── Entry point ────────────────────────────────────────
if __name__ == '__main__':

    if '--watch' in sys.argv:
        # Run forever on a schedule
        try:
            run_scheduler(interval_minutes=60)
        except KeyboardInterrupt:
            logger.info('Scheduler stopped by user')

    else:
        # Run just once
        count = fetch_all_feeds()
        print(f'\n✅ Done! Added {count} new articles to the database.')
