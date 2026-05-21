import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-12345')
    DB_PATH = 'data/'  # Папка с users.json и records.json

    BOT_TOKEN ='8869926258:AAFIu7asTVTVfZcmmxH3ZHlULOUqE38TGfY'
    CHAT_ID = '1490632841'

    BASE_URL = 'https://daily-slapping-elderly.ngrok-free.dev'
    DEBUG = True

