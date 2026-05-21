import hashlib
from datetime import datetime

class User:
    def __init__(self, user_id, username, password_hash, role, created_at=None):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin' или 'user'
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.password_hash == self.hash_password(password)

    def to_dict(self):
        """Превращает объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Восстанавливает объект User из словаря JSON."""
        return cls(
            user_id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            role=data["role"],
            created_at=data["created_at"]
        )