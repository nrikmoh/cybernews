# models.py
# ─────────────────────────────────────────────────────────
# Database models for CyberNews.
#
# Each class here represents one TABLE in the database.
# Each attribute represents one COLUMN in that table.
#
# SQLAlchemy turns Python objects into database rows
# automatically — we never write raw SQL.
# ─────────────────────────────────────────────────────────

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance.
# We don't connect it to the app yet — that happens in
# create_app() using the "init_app" pattern.
# This avoids circular imports.
db = SQLAlchemy()


# ═══════════════════════════════════════════════════════
# ARTICLE MODEL
# Represents the 'articles' table in the database.
# ═══════════════════════════════════════════════════════
class Article(db.Model):
    """
    Stores cybersecurity news articles.
    
    Each instance of this class = one row in the articles table.
    """

    # __tablename__ sets the actual table name in the database.
    # If you don't set it, SQLAlchemy uses the class name in lowercase.
    __tablename__ = 'articles'

    # ── Columns ──────────────────────────────────────────
    
    # PRIMARY KEY: unique identifier for each article
    # autoincrement=True means the database assigns the number
    id = db.Column(
        db.Integer,
        primary_key   = True,
        autoincrement = True,
    )

    # TITLE: the headline
    # nullable=False means this field is required (can't be empty)
    title = db.Column(
        db.String(300),
        nullable = False,
    )

    # SUMMARY: short description shown on cards
    summary = db.Column(
        db.Text,
        nullable = False,
    )

    # BODY: full article text
    body = db.Column(
        db.Text,
        nullable = False,
        default  = '',
    )

    # CATEGORY: which section this belongs to
    category = db.Column(
        db.String(50),
        nullable = False,
        index    = True,   # index makes filtering by category FAST
    )

    # SOURCE: where the news comes from
    source = db.Column(
        db.String(100),
        nullable = False,
        default  = 'CyberNews',
    )

    # IMAGE_URL: link to the article's header image
    image_url = db.Column(
        db.String(500),
        nullable = True,    # nullable=True means optional
        default  = 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
    )

    # FEATURED: is this the main hero article?
    # Boolean = True or False
    featured = db.Column(
        db.Boolean,
        default  = False,
        nullable = False,
    )

    # PUBLISHED: is the article visible to the public?
    # We can save drafts that aren't published yet
    published = db.Column(
        db.Boolean,
        default  = True,
        nullable = False,
    )

    # TAGS: stored as comma-separated string
    # e.g. "Windows,Zero-Day,CVE,Microsoft"
    # (In a production app you'd use a separate tags table)
    tags_string = db.Column(
        db.String(300),
        default  = '',
    )

    # CREATED_AT: when was the article added to the database?
    # datetime.utcnow is called without () so SQLAlchemy
    # calls it at the moment of insertion, not at class definition
    created_at = db.Column(
        db.DateTime,
        default  = datetime.utcnow,
        nullable = False,
    )

    # UPDATED_AT: when was it last edited?
    updated_at = db.Column(
        db.DateTime,
        default  = datetime.utcnow,
        onupdate = datetime.utcnow,  # auto-updates on every save
    )

    # ── Properties ───────────────────────────────────────
    # Properties look like attributes but run code

    @property
    def tags(self):
        """
        Convert the comma-separated tags_string into a Python list.
        Usage: article.tags → ['Windows', 'Zero-Day', 'CVE']
        """
        if not self.tags_string:
            return []
        return [t.strip() for t in self.tags_string.split(',') if t.strip()]

    @tags.setter
    def tags(self, tag_list):
        """
        Convert a Python list back to comma-separated string for storage.
        Usage: article.tags = ['Windows', 'Zero-Day']
        """
        if isinstance(tag_list, list):
            self.tags_string = ', '.join(tag_list)
        else:
            self.tags_string = tag_list or ''

    @property
    def read_time(self):
        """
        Calculate estimated reading time from body word count.
        Average reading speed: 200 words per minute.
        """
        word_count = len(self.body.split()) if self.body else 0
        minutes    = max(1, round(word_count / 200))
        return f"{minutes} min read"

    @property
    def formatted_date(self):
        """
        Format the created_at timestamp for display.
        Returns e.g. "Dec 25, 2025"
        """
        return self.created_at.strftime('%b %d, %Y')

    @property
    def image(self):
        """Alias so templates can use article.image like before."""
        return self.image_url

    # ── String representation ─────────────────────────────
    def __repr__(self):
        """
        What Python shows when you print an Article object.
        Useful for debugging.
        """
        return f'<Article {self.id}: {self.title[:50]}>'

    # ── Dictionary conversion ─────────────────────────────
    def to_dict(self):
        """
        Convert article to a Python dictionary.
        Used for JSON API responses.
        """
        return {
            'id':         self.id,
            'title':      self.title,
            'summary':    self.summary,
            'category':   self.category,
            'source':     self.source,
            'image':      self.image_url,
            'featured':   self.featured,
            'tags':       self.tags,
            'date':       self.formatted_date,
            'read_time':  self.read_time,
            'url':        f'/article/{self.id}',
        }


# ═══════════════════════════════════════════════════════
# CATEGORY MODEL
# Stores category metadata (description, icon, color)
# ═══════════════════════════════════════════════════════
class Category(db.Model):
    __tablename__ = 'categories'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50),  nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    icon        = db.Column(db.String(50),  default='fa-tag')
    color       = db.Column(db.String(20),  default='primary')
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name}>'

    @property
    def article_count(self):
        """How many published articles are in this category."""
        return Article.query.filter_by(
            category  = self.name,
            published = True,
        ).count()


# ═══════════════════════════════════════════════════════
# NEWSLETTER MODEL
# Stores email subscriptions
# ═══════════════════════════════════════════════════════
class Newsletter(db.Model):
    __tablename__ = 'newsletter'

    id         = db.Column(db.Integer,     primary_key=True)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    active     = db.Column(db.Boolean,     default=True)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f'<Newsletter {self.email}>'

# ═══════════════════════════════════════════════════════
# USER MODEL
# Stores admin user accounts.
# Flask-Login requires specific methods on this class.
# ═══════════════════════════════════════════════════════
class User(db.Model):
    """
    Admin user accounts for CyberNews.
    
    Flask-Login needs four things from this class:
    - is_authenticated  → is user logged in?
    - is_active         → is account enabled?
    - is_anonymous      → is this a guest?
    - get_id()          → return user's unique ID
    
    We get all of these for free by importing UserMixin.
    """

    __tablename__ = 'users'

    id         = db.Column(db.Integer,     primary_key=True)
    username   = db.Column(db.String(50),  nullable=False, unique=True)
    email      = db.Column(db.String(120), nullable=False, unique=True)

    # We NEVER store the real password — only the hash
    password_hash = db.Column(db.String(255), nullable=False)

    # Role: 'admin' or 'editor'
    role       = db.Column(db.String(20),  default='admin')

    # Is the account active? Admins can deactivate accounts.
    is_active  = db.Column(db.Boolean,     default=True)

    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    last_login = db.Column(db.DateTime,    nullable=True)

    # ── Flask-Login required properties ──────────────
    @property
    def is_authenticated(self):
        """Return True if user is logged in."""
        return True

    @property
    def is_anonymous(self):
        """Return False — this is a real user."""
        return False

    def get_id(self):
        """
        Return the user's ID as a string.
        Flask-Login uses this to store the user in the session.
        Must return a STRING, not an integer.
        """
        return str(self.id)

    # ── Password methods ──────────────────────────────
    def set_password(self, password):
        """
        Hash and store a password.
        We NEVER store the plain text password.
        
        bcrypt.generate_password_hash() returns bytes,
        we decode to string for storage in the database.
        """
        from app import bcrypt
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

    def check_password(self, password):
        """
        Verify a password attempt against the stored hash.
        
        bcrypt.check_password_hash() does the comparison safely.
        Returns True if the password matches, False otherwise.
        """
        from app import bcrypt
        return bcrypt.check_password_hash(
            self.password_hash,
            password,
        )

    def update_last_login(self):
        """Record when the user last logged in."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


# ═══════════════════════════════════════════════════════
# LOGIN AUDIT LOG
# Records every login attempt for security monitoring
# ═══════════════════════════════════════════════════════
class LoginLog(db.Model):
    """
    Records every login attempt.
    
    This lets us:
    - Detect brute force attacks
    - See when and where admins logged in
    - Alert on suspicious activity
    """

    __tablename__ = 'login_logs'

    id         = db.Column(db.Integer,     primary_key=True)
    username   = db.Column(db.String(50),  nullable=False)
    ip_address = db.Column(db.String(45),  nullable=False)  # 45 supports IPv6
    user_agent = db.Column(db.String(200), nullable=True)
    success    = db.Column(db.Boolean,     nullable=False)
    timestamp  = db.Column(db.DateTime,    default=datetime.utcnow)

    # Optional: link to the user if login succeeded
    user_id    = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    def __repr__(self):
        status = 'SUCCESS' if self.success else 'FAILED'
        return f'<LoginLog {status} {self.username} {self.timestamp}>'

    @classmethod
    def record(cls, username, ip, user_agent, success, user_id=None):
        """
        Class method to easily record a login attempt.
        
        Usage:
            LoginLog.record(
                username   = 'hassan',
                ip         = '1.2.3.4',
                user_agent = request.headers.get('User-Agent'),
                success    = True,
                user_id    = user.id,
            )
        """
        log = cls(
            username   = username,
            ip_address = ip,
            user_agent = (user_agent or '')[:200],
            success    = success,
            user_id    = user_id,
        )
        db.session.add(log)
        db.session.commit()
        return log
