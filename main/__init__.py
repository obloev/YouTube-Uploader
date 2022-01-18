import logging
from telethon import TelegramClient
from os import getenv

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

API_ID = int(getenv('API_ID'))
API_HASH = getenv('API_HASH')
BOT_TOKEN = getenv('BOT_TOKEN')
MONGODB_URI = getenv('MONGODB_URI')
ADMIN = int(getenv('ADMIN'))
HEROKU_API = getenv('HEROKU_API')
HEROKU_APP = getenv('HEROKU_APP')
CHANNEL = getenv('CHANNEL')
JOINCHAT_LINK = getenv('JOINCHAT_LINK')
GROUP_ID = int(getenv('GROUP_ID'))
BOT_UN = getenv('BOT_UN')
RESTART_TEXT = '♻️ RESTART'
POST_TEXT = '📝 CREATE POST'
USERS_COUNT_TEXT = '👤 USERS COUNT'
TOP_USERS_TEXT = '🌟 TOP USERS'
CANCEL_TEXT = '❌ CANCEL'

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
