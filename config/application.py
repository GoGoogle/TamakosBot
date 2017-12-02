import os

# COMMON CONFIG

BOT_TOKEN = "334635714:AAFglddZSt7oROLLRLL9JuzMdLvx-uW-09A"
# BOT_TOKEN = "425909661:AAHC_a9-htfYsjaZuKfP6jjcl8n2sjizctg"

ADMINS = [423453012]

FILE_TRANSFER_TIMEOUT = 300

CHUNK_SIZE = 1024 * 1024

TMP_Folder = 'tmp'

LOG_FILE = 'LOG'

WEBHOOK_LOCAL = {
    'listen': '127.0.0.1',
    'port': 5000,
    'url_path': 'bottoken'
}

WEBHOOK_REMOTE = {
    'url': 'https://telegram.lemo.site/bottoken',
    'timeout': 40
}

# MUSIC CONFIG

COOKIE_PATH = os.path.join(TMP_Folder, 'cookie')

NETEASE_LOGIN_PAYLOAD = {
    'username': 'xxxxxx',
    'password': 'xxxxxx'
}
