class Record:
    def __init__(self, record_id, user_id, name, age, group, gpa):
        self.id = int(record_id)
        self.user_id = int(user_id)  # Связь с аккаунтом из users.json
        self.name = name
        self.age = int(age)
        self.group = group
        self.gpa = float(gpa)

    def to_dict(self):
        """Преобразует объект студента в словарь для записи в records.json."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "group": self.group,
            "gpa": self.gpa
        }

    @classmethod
    def from_dict(cls, data):
        """Восстанавливает объект Record из сохраненного в JSON словаря (Требование Task 1)."""
        return cls(
            record_id=data["id"],
            user_id=data["user_id"],
            name=data["name"],
            age=data["age"],
            group=data["group"],
            gpa=data["gpa"]
        )