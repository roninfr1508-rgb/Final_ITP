from flask import session, redirect, url_for, abort
from functools import wraps
from services.db_service import DatabaseService
from models.user import User
from services.bot_service import BotService

db = DatabaseService()


def login_required(role=None):

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #Проверяем вошел ли пользователь в систему
            if 'user_id' not in session:
                return redirect(url_for('login_route'))

            if role == 'admin' and session.get('role') != 'admin':
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class AuthController:
    @staticmethod
    def login(username, password):
        users = db.load_users()
        user = next((u for u in users if u.username == username), None)

        if user and user.check_password(password):
            # Записываем данные в сессию
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return True
        return False

    @staticmethod
    def register(username, password):
        users = db.load_users()

        if any(u.username == username for u in users):
            return False, "Username already exists"

        new_id = max([u.id for u in users], default=0) + 1
        password_hash = User.hash_password(password)

        new_user = User(new_id, username, password_hash, role='user')
        db.save_user(new_user)

        BotService.notify_new_user(username)
        return True, "Success"

    @staticmethod
    def logout():
        session.clear()