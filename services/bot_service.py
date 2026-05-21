import telebot
import logging
from config import Config


class BotService:
    # Инициализируем бота точно так же, как в твоем ассаименте,
    # но берем токен из нашего единого класса конфигурации
    _bot = telebot.TeleBot(Config.BOT_TOKEN) if Config.BOT_TOKEN else None

    @classmethod
    def _send_message(cls, text):
        """
        Внутренний синхронный метод для отправки уведомлений.
        Использует твою библиотеку telebot.
        """
        if not cls._bot or not Config.CHAT_ID:
            logging.warning("Telegram Bot Credentials are not configured in config.py")
            return

        try:
            # Отправляем сообщение в чат администратора (синхронный вызов)
            cls._bot.send_message(Config.CHAT_ID, text)
        except Exception as e:
            # КРИТИЧЕСКОЕ ТРЕБОВАНИЕ TASK 6:
            # Если токен неверный или лег интернет — просто пишем ошибку в консоль.
            # Flask-сайт ни в коем случае не должен упасть!
            logging.error(f"Telegram Notification Failed: {e}")

    @classmethod
    def notify_new_user(cls, username):
        """Вызывается в AuthController при регистрации нового аккаунта."""
        cls._send_message(f"🔔 New user registered: {username}")

    @classmethod
    def notify_admin_action(cls, action, detail):
        """Вызывается в AdminController при действиях админа (создание/удаление пользователей)."""
        cls._send_message(f"🛠️ Admin Action - {action}: {detail}")