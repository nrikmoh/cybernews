# CyberNews — Cybersecurity Intelligence Daily

> "Never stop learning in a world that never sleeps." — Mohsen

A professional cybersecurity news aggregator built from scratch as a two-week learning project.

## Live Website

**https://cyber-news.duckdns.org**

## Features

### Public
- Real-time news from 5 trusted RSS sources (auto-updates hourly)
- Dedicated search page with full-text database search
- 6 categories: Malware, Data Breaches, Vulnerabilities, Privacy, Research, Threats
- Dark/Light mode toggle
- Mobile responsive design
- Alerts dropdown with latest articles
- Konami Code easter egg

### Admin Panel
- Analytics dashboard (visitors, devices, browsers, top pages)
- Article management (create, edit, delete, publish/draft)
- User authentication with login history
- Live security monitor
- Newsletter subscribers management
- Security audit log

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3.12, Flask |
| Database | SQLite and SQLAlchemy |
| Auth | Flask-Login and bcrypt |
| Security | Flask-Limiter, CSP, CSRF |
| Web Server | Nginx |
| App Server | Gunicorn (4 workers) |
| HTTPS | Lets Encrypt |
| OS | Ubuntu VPS |

## Project Structure

    cybernews/
    ├── app.py              # Application factory
    ├── config.py           # Configuration
    ├── models.py           # Database models
    ├── forms.py            # WTForms
    ├── rss_fetcher.py      # RSS auto-fetcher
    ├── routes/
    │   ├── main.py         # Public routes
    │   ├── admin.py        # Admin panel
    │   ├── auth.py         # Authentication
    │   └── errors.py       # Error handlers
    ├── templates/          # 28 Jinja2 templates
    ├── static/             # CSS, JS, images
    └── requirements.txt

## Security

- bcrypt password hashing
- CSRF protection on all forms
- Brute force login protection (5 attempts lockout)
- Rate limiting
- 6 HTTP security headers
- Content Security Policy
- 20 plus attack paths blocked
- SQL injection prevention
- Login audit logging

## RSS Sources

- The Hacker News
- Krebs on Security
- Bleeping Computer
- Dark Reading
- SecurityWeek

## Quick Start

    git clone https://github.com/nrikmoh/cybernews.git
    cd cybernews
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python seed_db.py
    python create_admin.py
    python rss_fetcher.py
    python app.py

## Author

**Mohsen** — Germany

Built with love and Python
