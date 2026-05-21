import os
import json
from models.user import User
from models.record import Record
from config import Config


class DatabaseService:
    def __init__(self):
        self.base_path = Config.DB_PATH
        self.users_file = os.path.join(self.base_path, 'users.json')
        self.records_file = os.path.join(self.base_path, 'records.json')

        # Автоматически создаем папку базы данных, если её нет
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        self._init_db()

    def _init_db(self):
        """Первоначальное заполнение (seed) базы данных тестовыми аккаунтами."""
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            # Seed-данные согласно требованиям ТЗ (admin/admin123 и testuser/user123)
            admin_hash = User.hash_password("admin123")
            user_hash = User.hash_password("user123")

            default_users = [
                User(1, "admin", admin_hash, "admin").to_dict(),
                User(2, "testuser", user_hash, "user").to_dict()
            ]
            self._write_file(self.users_file, default_users)

        if not os.path.exists(self.records_file):
            self._write_file(self.records_file, [])

    def _read_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_file(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # === Методы для работы с Users ===
    def load_users(self):
        """Чтение всех пользователей и реконструкция их в объекты User."""
        data = self._read_file(self.users_file)
        return [User.from_dict(u) for u in data]

    def save_user(self, user_obj):
        """Сохранение или обновление пользователя."""
        users = self.load_users()
        users_dict = [u.to_dict() if u.id != user_obj.id else user_obj.to_dict() for u in users]
        if not any(u['id'] == user_obj.id for u in users_dict):
            users_dict.append(user_obj.to_dict())
        self._write_file(self.users_file, users_dict)

    def delete_user(self, user_id):
        """Удаление пользователя и каскадное удаление его записей."""
        users = self.load_users()
        updated_users = [u.to_dict() for u in users if u.id != int(user_id)]
        self._write_file(self.users_file, updated_users)

        # Каскадное удаление записей студентов этого пользователя
        self.delete_records_by_user(user_id)

    # === Методы для работы со Студентами (Records) ===
    def load_records(self):
        """Чтение всех студентов и реконструкция их в объекты Record."""
        data = self._read_file(self.records_file)
        return [Record.from_dict(r) for r in data]

    def save_record(self, record_obj):
        """Сохранение новой записи студента."""
        records = self.load_records()
        records.append(record_obj)
        self._write_file(self.records_file, [r.to_dict() for r in records])

    def delete_records_by_user(self, user_id):
        """Удаление всех студентов, принадлежащих конкретному user_id."""
        records = self.load_records()
        updated_records = [r.to_dict() for r in records if r.user_id != int(user_id)]
        self._write_file(self.records_file, updated_records)