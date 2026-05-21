from services.db_service import DatabaseService
from services.bot_service import BotService
from models.user import User

db = DatabaseService()


class AdminController:
    @staticmethod
    def get_dashboard_data():
        """
        Собирает статистику для главного экрана админ-панели (Task 3).
        """
        users = db.load_users()
        records = db.load_records()

        # Сортируем пользователей по дате создания, чтобы показать 5 последних
        recent_users = sorted(users, key=lambda x: x.created_at, reverse=True)[:5]

        return {
            "total_users": len(users),
            "total_records": len(records),
            "recent_users": recent_users
        }

    @staticmethod
    def list_users():
        """Возвращает список всех пользователей системы."""
        return db.load_users()

    @staticmethod
    def create_user(username, password, role):
        """Создание админом нового аккаунта прямо из панели."""
        users = db.load_users()
        if any(u.username == username for u in users):
            return False

        new_id = max([u.id for u in users], default=0) + 1
        pw_hash = User.hash_password(password)

        new_user = User(new_id, username, pw_hash, role)
        db.save_user(new_user)

        # Уведомляем бота о действии админа
        BotService.notify_admin_action("CREATE_USER", f"Admin created user '{username}' with role '{role}'")
        return True

    @staticmethod
    def delete_user(current_admin_id, target_user_id):
        """
        Удаление пользователя бэкендом.
        Включает проверку: админ не может удалить сам себя!
        """
        if int(current_admin_id) == int(target_user_id):
            return False

        db.delete_user(target_user_id)

        # Уведомляем бота об удалении
        BotService.notify_admin_action("DELETE_USER", f"Admin deleted user ID: {target_user_id}")
        return True

    @staticmethod
    def list_all_records_paginated(page, per_page=10):
        """
        Возвращает список ВСЕХ студентов в системе с пагинацией по 10 штук на страницу.
        """
        all_records = db.load_records()
        start = (page - 1) * per_page
        end = start + per_page

        paginated_records = all_records[start:end]
        total_pages = (len(all_records) + per_page - 1) // per_page

        return paginated_records, total_pages