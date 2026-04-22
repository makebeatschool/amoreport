import os
import json
import requests
from config import DEF_FILE, BASE_DOMAIN, CLIENT_ID, CLIENT_SECRET, AUTH_CODE, REDIRECT_URL

def load_token(type=0,  file_path=DEF_FILE):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if not type:
            return data['access_token']
        return data['refresh_token']
def save_tokens(access_token=None, refresh_token=None, file_path=DEF_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                tokens = json.load(f)
            except json.JSONDecodeError:
                tokens = {}
    else:
        tokens = {}
    if access_token is not None:
        tokens["access_token"] = access_token
    else:
        tokens.setdefault("access_token", "")

    if refresh_token is not None:
        tokens["refresh_token"] = refresh_token
    else:
        tokens.setdefault("refresh_token", "")
    tokens.setdefault("access_token", "")
    tokens.setdefault("refresh_token", "")
    with open(file_path, "w") as f:
        json.dump(tokens, f, indent=2)

def get_tokens():
    url = f"{BASE_DOMAIN}/oauth2/access_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "redirect_uri": REDIRECT_URL
    }
    tokens = requests.post(url, json=data).json()
    if "access_token" not in tokens:
        print("AUTH CODE НЕВАЛИДЕН — пересоздай его")
        return False
    save_tokens(tokens['access_token'], tokens["refresh_token"])
    return True
def refresh_token():
    refresh_token = load_token(1)
    url = f"{BASE_DOMAIN}/oauth2/access_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": REDIRECT_URL
    }
    new_tokens = requests.post(url, json=data).json()
    save_tokens(access_token=new_tokens["access_token"], refresh_token=new_tokens["refresh_token"])
    return True

