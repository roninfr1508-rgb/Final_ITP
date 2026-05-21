from services.db_service import DatabaseService
from models.record import Record
from models.user import User

db = DatabaseService()


class UserController:
    @staticmethod
    def get_my_records(user_id):
        """
        Фильтрация: получить студентов, принадлежащих ТОЛЬКО текущему пользователю.
        """
        all_records = db.load_records()
        return [r for r in all_records if r.user_id == int(user_id)]

    @staticmethod
    def add_record(user_id, name, age, group, gpa):
        """
        Добавление нового студента с жесткой привязкой к user_id создателя.
        """
        records = db.load_records()
        new_id = max([r.id for r in records], default=0) + 1

        new_student = Record(new_id, int(user_id), name, age, group, gpa)
        db.save_record(new_student)

    @staticmethod
    def get_profile_info(user_id):
        """
        Собирает данные для страницы профиля (Task 4): имя, роль, дата создания
        и общее количество студентов, добавленных этим пользователем.
        """
        users = db.load_users()
        user = next((u for u in users if u.id == int(user_id)), None)

        if user:
            my_records_count = len(UserController.get_my_records(user_id))
            return {
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at,
                "record_count": my_records_count
            }
        return None

    @staticmethod
    def update_password(user_id, new_password):
        """
        Смена пользователем своего пароля с хэшированием в SHA-256.
        """
        users = db.load_users()
        user = next((u for u in users if u.id == int(user_id)), None)

        if user:
            user.password_hash = User.hash_password(new_password)
            db.save_user(user)
            return True
        return False