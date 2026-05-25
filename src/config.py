import os

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEF_FILE = os.path.join(PARENT_DIR, '', 'tokens.json')

# ========= Base =======================
BASE_DOMAIN = "https://makebeatschool.amocrm.ru"
REDIRECT_URL = "https://example.com"

# ======  dev  ======================
TELEGRAM_DOMEN = "https://api.telegram.org"

# ======  prod  ====================
# TELEGRAM_DOMEN = "https://white-block-333b.nefarionys.workers.dev"

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://makebeatschool.amocrm.ru',
    'referer': 'https://makebeatschool.amocrm.ru/events/list/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


# Константы
CALL_SHORT_MAX = 10
CALL_MEDIUM_MAX = 30
UNIQUE_DIALOG_MIN_DURATION = 25
NEW_LEAD_MAX_CALLS = 3
