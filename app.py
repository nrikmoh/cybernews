# app.py - CyberNews Flask Application

from flask import Flask, render_template

app = Flask(__name__)

# ─────────────────────────────────────────
# Sample news data (temporary - later this
# will come from a real database)
# ─────────────────────────────────────────
articles = [
    {
        "id": 1,
        "title": "Critical Zero-Day Vulnerability Found in Windows Kernel",
        "summary": "Security researchers have discovered a critical zero-day vulnerability affecting all modern versions of Windows, allowing attackers to gain SYSTEM privileges.",
        "category": "Vulnerabilities",
        "source": "The Hacker News",
        "date": "Dec 25, 2025",
        "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
        "featured": True
    },
    {
        "id": 2,
        "title": "Major Data Breach Exposes 50 Million User Records",
        "summary": "A leading social media platform suffered a massive data breach, exposing personal information including emails, phone numbers, and hashed passwords.",
        "category": "Data Breaches",
        "source": "SecurityWeek",
        "date": "Dec 24, 2025",
        "image": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80",
        "featured": False
    },
    {
        "id": 3,
        "title": "New Ransomware Strain Targets Healthcare Sector",
        "summary": "A sophisticated ransomware group has launched a coordinated attack against hospital networks across Europe, encrypting patient records and demanding millions.",
        "category": "Malware",
        "source": "Krebs on Security",
        "date": "Dec 24, 2025",
        "image": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80",
        "featured": False
    },
    {
        "id": 4,
        "title": "FBI Warns of Surge in AI-Powered Phishing Attacks",
        "summary": "The FBI has issued an urgent warning about a dramatic increase in AI-generated phishing emails that are nearly indistinguishable from legitimate communications.",
        "category": "Threats",
        "source": "FBI Cyber Division",
        "date": "Dec 23, 2025",
        "image": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
        "featured": False
    },
    {
        "id": 5,
        "title": "NSA Releases New Guidelines for Quantum-Safe Encryption",
        "summary": "The National Security Agency published comprehensive guidelines for organizations to begin transitioning to post-quantum cryptographic algorithms before 2030.",
        "category": "Research",
        "source": "NSA",
        "date": "Dec 23, 2025",
        "image": "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80",
        "featured": False
    },
    {
        "id": 6,
        "title": "Privacy Regulators Fine Tech Giant $2.3 Billion",
        "summary": "European privacy regulators issued a record-breaking fine against a major tech company for systematic violations of GDPR data protection rules.",
        "category": "Privacy",
        "source": "Reuters",
        "date": "Dec 22, 2025",
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80",
        "featured": False
    },
    {
        "id": 7,
        "title": "Chinese APT Group Targets Government Infrastructure",
        "summary": "A state-sponsored Chinese hacking group has been linked to a series of intrusions targeting government networks in Southeast Asia using novel malware.",
        "category": "Threats",
        "source": "Mandiant",
        "date": "Dec 22, 2025",
        "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
        "featured": False
    },
    {
        "id": 8,
        "title": "Open Source Security Tool Gains Massive Adoption",
        "summary": "A newly released open source penetration testing framework has been downloaded over 2 million times in its first month, becoming the go-to tool for security professionals.",
        "category": "Research",
        "source": "GitHub Security",
        "date": "Dec 21, 2025",
        "image": "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80",
        "featured": False
    },
    {
        "id": 9,
        "title": "Supply Chain Attack Compromises 500 npm Packages",
        "summary": "Attackers successfully injected malicious code into hundreds of popular npm packages, potentially affecting millions of JavaScript developers worldwide.",
        "category": "Malware",
        "source": "Snyk Security",
        "date": "Dec 21, 2025",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80",
        "featured": False
    }
]

# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.route('/')
def home():
    featured = next((a for a in articles if a['featured']), articles[0])
    regular = [a for a in articles if not a['featured']]
    return render_template('index.html',
                           articles=articles,
                           featured=featured,
                           regular=regular)

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/article/<int:article_id>')
def article(article_id):
    post = next((a for a in articles if a['id'] == article_id), None)
    if post is None:
        return "Article not found", 404
    return render_template('article.html', article=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
