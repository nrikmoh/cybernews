# CyberNews — Project Summary

## Student Information
- **Name:** Mohsen
- **Location:** Germany
- **Date:** July 2026

## Live Website
**https://cyber-news.duckdns.org**

## GitHub Repository
**https://github.com/nrikmoh/cybernews**

---

## 1. Project Overview

CyberNews is a cybersecurity news aggregation platform that collects,
organizes, and presents security news from trusted sources in one place.

The website was built from scratch over two weeks as a learning project,
progressing from basic HTML to a fully deployed production application.

---

## 2. Main Features

### Public Website
- Homepage with featured story, article grid, and sidebar
- Real-time news from 5 RSS sources (auto-updates every hour)
- 6 categories: Malware, Data Breaches, Vulnerabilities, Privacy, Research, Threats
- Dedicated search page with full-text database search
- Individual article pages with related stories
- Categories page with live article counts
- Breaking news ticker with real headlines
- Dynamic threat level indicator based on real data
- Live security monitor showing real-time activity
- Dark/light mode toggle
- Alerts dropdown with latest articles
- Pagination (10 articles per page)
- Newsletter subscription
- Contact form with message storage
- Privacy Policy, Terms of Use, and Contact pages
- Mobile responsive design
- Konami Code easter egg

### Admin Panel
- Dashboard with article, visitor, and security statistics
- Article management (create, edit, delete, publish/draft)
- Visitor analytics (views, devices, browsers, top pages, referrers)
- Security audit log (login attempts, blocked attacks)
- Newsletter subscriber management
- Contact message inbox
- Manual RSS fetch trigger

---

## 3. Technologies Used

### Frontend
| Technology | Purpose |
|-----------|---------|
| HTML5 | Page structure and semantic markup |
| CSS3 | Styling, animations, responsive design |
| JavaScript | Interactive features, search, filtering, animations |
| Google Fonts | Typography (Inter, JetBrains Mono) |
| Font Awesome | Icons |

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.12 | Server-side programming language |
| Flask | Web framework |
| SQLAlchemy | Database ORM |
| Flask-Login | User authentication |
| Flask-Bcrypt | Password hashing |
| Flask-WTF | Form handling and CSRF protection |
| Flask-Limiter | Rate limiting |
| Flask-Compress | Response compression |
| Feedparser | RSS feed parsing |
| Jinja2 | HTML template engine |

### Database
| Technology | Purpose |
|-----------|---------|
| SQLite | Relational database |
| 6 models | Articles, Users, Categories, Newsletter, LoginLog, PageView, ContactMessage |
| 9 indexes | Performance optimization |

### Deployment
| Technology | Purpose |
|-----------|---------|
| Ubuntu VPS | Server operating system |
| Nginx | Web server and reverse proxy |
| Gunicorn | Python WSGI application server (4 workers) |
| Let's Encrypt | Free SSL/TLS certificate (HTTPS) |
| Systemd | Process management and auto-restart |
| Cron | Scheduled tasks (RSS fetch, database backup) |
| UFW | Firewall |
| Fail2ban | Automatic IP banning |

---

## 4. Architecture

    Internet (Users)
        |
        v
    HTTPS (Let's Encrypt SSL)
        |
        v
    Nginx (Port 80/443)
    - Serves static files directly
    - Rate limiting
    - Bad bot blocking
    - Reverse proxy
        |
        v
    Gunicorn (Port 8000, 4 workers)
    - Production WSGI server
    - Auto-restarts on crash
        |
        v
    Flask Application
    - Routes (main, admin, auth, errors)
    - Security middleware
    - Template rendering
        |
        v
    SQLite Database
    - Articles, Users, Analytics
    - Contact messages
    - Login audit log

---

## 5. Security Features

| Feature | Implementation |
|---------|---------------|
| Password hashing | bcrypt with salt |
| CSRF protection | Flask-WTF tokens on all forms |
| Brute force protection | 5 attempts then 15 min lockout |
| Rate limiting | Nginx + Flask-Limiter |
| Security headers | CSP, X-Frame-Options, HSTS, etc. |
| Attack path blocking | 20+ scanner paths blocked |
| Bot detection | User-Agent filtering |
| SQL injection prevention | Parameterized queries + URL scanning |
| Input sanitization | HTML escaping, length limits |
| Login audit log | Every attempt recorded |
| IP banning | Fail2ban auto-ban |
| HTTPS | Let's Encrypt certificate |
| File permissions | 600 for .env and database |

---

## 6. AI Prototype vs Final Website

### AI Prototype (Bolt.new)
- Generated a static mockup in minutes
- Dark-themed cybersecurity design
- Static content, no backend
- No database, no authentication
- No real news data

### Final Website (Built from scratch)
- Full Flask backend with database
- Real-time RSS news from 5 sources
- User authentication with bcrypt
- Admin panel with full CRUD
- Analytics dashboard
- Security hardening
- Production deployment with Nginx + Gunicorn
- HTTPS with Let's Encrypt

### Key Differences
The AI prototype showed what the end result could look like.
The final website is a fully functional, secure, production-grade
application that was built step by step over two weeks.

---

## 7. Project Statistics

| Metric | Value |
|--------|-------|
| Lines of Python | 2,000+ |
| Lines of CSS | 3,500+ |
| Lines of JavaScript | 1,000+ |
| HTML Templates | 28 |
| Routes | 15+ |
| Database Models | 7 |
| Database Indexes | 9 |
| Security Checks | 20+ |
| RSS Sources | 5 |
| Local Images | 191 |
| Build Time | 2 weeks |

---

## 8. Challenges

The hardest part was connecting all the different pieces of the puzzle.
Each technology (HTML, CSS, JavaScript, Python, Flask, SQL) made sense
individually, but making them all work together — and keeping everything
secure — was the real challenge.

Specific challenges included:
- Database schema design and migrations
- CSRF protection across different form types
- Mobile responsive design
- Nginx and Gunicorn configuration
- SSL certificate setup
- Rate limiting without blocking real users
- Image management for 150+ articles

---

## 9. What I Learned

- Full-stack web development from HTML to deployment
- Python and Flask web framework
- Database design with SQLAlchemy
- User authentication and session management
- Web security best practices (OWASP Top 10)
- Linux server administration
- Nginx web server configuration
- Git version control
- RSS feed parsing and content aggregation
- Responsive design for mobile devices

---

## 10. Future Improvements

- Add email sending for newsletter
- Implement article commenting system
- Add user registration (not just admin)
- Integrate more RSS sources
- Add real-time WebSocket notifications
- Implement full-text search with ranking
- Add article bookmarking for users
- Create a mobile app version

---

## Author

**Mohsen** — Germany
