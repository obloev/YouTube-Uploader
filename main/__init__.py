import logging
from telethon import TelegramClient
from decouple import config

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

API_ID = config('API_ID', default=None, cast=int)
API_HASH = config('API_HASH', default=None)
BOT_TOKEN = config('BOT_TOKEN', default=None)
MONGODB_URI = config('MONGODB_URI', default=None)
ADMIN = config('ADMIN', default=None, cast=int)
CHANNEL = config('CHANNEL', default=None)
JOINCHAT_LINK = config('JOINCHAT_LINK', default=None)
GROUP_ID = config('GROUP_ID', default=None, cast=int)
BOT_UN = config('BOT_UN', default=None)
POST_TEXT = '📝 CREATE POST'
USERS_COUNT_TEXT = '👤 USERS COUNT'
TOP_USERS_TEXT = '🌟 TOP USERS'
CANCEL_TEXT = '❌ CANCEL'

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
