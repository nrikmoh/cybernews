from app import app
from models import db, User

with app.app_context():
    # Show existing users
    users = User.query.all()
    print('\nExisting users:')
    for u in users:
        print(f'  - {u.username} ({u.email}) [{u.role}]')

    print()
    username = input('Username to update: ')
    user = User.query.filter_by(username=username).first()

    if user:
        new_pw = input('New password (min 8 chars): ')
        if len(new_pw) >= 8:
            user.set_password(new_pw)
            db.session.commit()
            print(f'\n✅ Password updated for {username}')
        else:
            print('\n❌ Password too short!')
    else:
        print(f'\n❌ User "{username}" not found')
