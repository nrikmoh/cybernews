#!/bin/bash
# ─────────────────────────────────────────────────────────
# CyberNews Setup Script
# Run this after cloning to set up the project
# Usage: bash setup.sh
# ─────────────────────────────────────────────────────────

echo "🛡️  CyberNews Setup"
echo "===================="

# Check Python
python3 --version || { echo "❌ Python 3 required"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env — please add your SECRET_KEY"
fi

# Create image directories
mkdir -p static/images/photos/{malware,breaches,vulnerabilities,privacy,threats,research,general}
mkdir -p static/images/fallback
mkdir -p backups

# Initialize database
echo "Setting up database..."
python seed_db.py

# Create admin user
echo ""
echo "Creating admin user..."
python create_admin.py

# Fetch initial articles
echo ""
echo "Fetching initial articles..."
python rss_fetcher.py

echo ""
echo "✅ Setup complete!"
echo "Run: python app.py"
echo "Visit: http://localhost:5000"
