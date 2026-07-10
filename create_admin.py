# create_admin.py
# ─────────────────────────────────────────────────────────
# Run this script ONCE to create your admin user account.
#
# Usage:
#   python create_admin.py
# ─────────────────────────────────────────────────────────

from app    import app, bcrypt
from models import db, User


def create_admin():
    with app.app_context():

        # Create tables if they don't exist yet
        db.create_all()

        # ── Get credentials from user ──────────────────
        print('\n🛡️  CyberNews Admin Account Setup')
        print('─' * 40)

        username = input('Enter admin username: ').strip()
        email    = input('Enter admin email: ').strip()
        password = input('Enter admin password: ').strip()

        # ── Validate input ─────────────────────────────
        if not username or not email or not password:
            print('❌ All fields are required.')
            return

        if len(password) < 8:
            print('❌ Password must be at least 8 characters.')
            return

        if '@' not in email:
            print('❌ Please enter a valid email.')
            return

        # ── Check if username already exists ───────────
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f'❌ Username "{username}" already exists.')
            return

        # ── Create the user ────────────────────────────
        user = User(
            username = username,
            email    = email,
            role     = 'admin',
            is_active = True,
        )

        # Hash the password before storing
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f'''
╔══════════════════════════════════════╗
║   ✅ Admin account created!          ║
╠══════════════════════════════════════╣
║  Username: {username:<29}║
║  Email:    {email:<29}║
║  Role:     admin                     ║
╠══════════════════════════════════════╣
║  Login at: /login                    ║
╚══════════════════════════════════════╝
        ''')


if __name__ == '__main__':
    create_admin()
