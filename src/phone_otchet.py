import requests
from datetime import date as dt
from collections import defaultdict

# date = "2026-05-23"
TELEGRAM_DOMEN = "https://api.telegram.org"
TELEGRAM_BOT_TOKEN="6283104932:AAGQrvcM8qI4_5DL0okJmKxQLIoVflWoVa0"
TELEGRAM_CHAT_ID="1785513479"
# TELEGRAM_BOT_TOKEN = "8078411503:AAEv6bx1rBg0yMDssgjbLRnFS8VE4YlV1mI"
# TELEGRAM_CHAT_ID = "-1003812558799"

login = "makebeatschool@gmail.com"
password = "J8wdnRDa"

url_uis_report = "https://uis-prod-msk-report-constructor-api.uiscom.ru/builder/report"
headers_uis = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://go.uiscom.ru",
    "Referer": "https://go.uiscom.ru/reports/calls/2300492",
    "User-Agent": "Mozilla/5.0"
}

def generate_payload(date, limit=1000):
    return  {
        "report_id": 2300492,
        "report_type": "calls",
        "date_from": f"{date} 00:00:00",
        "date_till": f"{date} 23:59:59",
        "fields": [
            "employees",
            "call_total_duration",
            "call_start_date_time",
            "call_talk_duration",
        ],
        "is_total_items_only": False,
        "limit": limit,
        "mode": "flat",
        "offset": 0,
        "sort": [
            {
                "field": "call_total_duration",
                "order": "desc"
            }
        ]
    }

def get_token():
    return "eyJhbGciOiJSUzI1NiIsImtpZCI6ImpQWmozdjdaLVVXUUZobE5PelVSZFNIUFFUVUxtWUUxdHJoQ0F5VnJqNkUiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiJmYzM4ZWUyZS0yNDhkLTQ2NTctYWMzMy0wNWVjMDVjZjk2ZjAiLCJzaWQiOiIwMDUwMDdlNjc5ZTA0MmIwOGY0MzE4ZjgzMjI1MjBkMyIsImlzcyI6Imh0dHBzOi8vdWlzLXByb2QtbXNrLXVjLXNzby1hcGkudWlzY29tLnJ1IiwiYXVkIjpbImh0dHBzOi8vdWlzLXByb2QtbXNrLXJlcG9ydC1jb25zdHJ1Y3Rvci1hcGkudWlzY29tLnJ1Il0sInN1YiI6IkNvbWFnaWNEQnx1aXMyfDEyODYwM3w4NTI2OTIiLCJzdWJkIjp7InByb2plY3QiOiJ1aXMyIiwiZGF0YV9jZW50ZXIiOiJtb3Njb3ciLCJhcHBfaWQiOjEyODYwMywiY3VzdG9tZXJfaWQiOjEwNDUzOTMsInVzZXJfaWQiOjg1MjY5MiwibG9naW4iOiJtYWtlYmVhdHNjaG9vbEBnbWFpbC5jb20iLCJ1c2VyX25hbWUiOiLQqNC60L7Qu9CwINCx0LjRgtCx0L7QutGB0LAgXCLQlNCw0LnQkdC40YJcIiBbQU1PQ1JNXSIsImlzX3N5c3RlbSI6ZmFsc2UsInRpbWV6b25lIjoiRXVyb3BlL01vc2NvdyIsImxjIjoicnUifSwiY2xpZW50X2lkIjoiaHR0cHM6Ly91aXMtcHJvZC1tc2stcmVwb3J0LWNvbnN0cnVjdG9yLWFwaS51aXNjb20ucnUiLCJpYXQiOjE3NzgyNDM5NzMsImFjdCI6eyJjbGllbnRfaWQiOiJodHRwczovL3Vpcy1wcm9kLW1zay11Yy1zc28tYXBpLnVpc2NvbS5ydSJ9LCJub3RfdHJ1c3RlZF9kZXZpY2UiOmZhbHNlfQ.piVHOp2UMsG4H9yNhNXfRoxRebcnQ410ruLRAiLemyXdgpX9YAJR8poQw8_0Yey8ELENq8Fxl-pG2kNhQrjx_hP01LeDtxwJrZJsk9qd5SmBlveH3S7IXWSD-K1RafWiu5vAim5gwYURhic72rlhnFrtxJ-lzPyoZFD4RUbSOYB8bgJDXh-Nj_WElcpiO2eyh-nk9tOe8aSjE0NirsnHKf27F3gTBPOq1sVNd-Kx8F9pMd2Lyd44JcR1NDM_wIvj0uHDChnH_CGb2HV9YIuH6z1KhA8jW3l0vmInvnvdoF4-G4Kp4hKUGjHTSakR1nHIH3OOIMADp_Qlqx-E-KDw0WJZlfDaloyfWt0lEUveoYbSqH2QkPAcENOEP45BVXlGQmVjOYAQVgNlSdGgy2jC0UclG9Th251LED0QWaHW5vYD58zNi1h3f9CW56ahHj8vDylVrHMiQO_CA55AQRxchug7qD8TkC6yBUE56i_Ag7xfEBHFT5y_WsITFtgEWsr2w1kj12O5nH3KribX4_A8_ffRvTRvdDfFdOC7UTWdvEYzQ0YbrjxJ7_2TnJ6isKVMjmMpBxkudYMw93u0oPd8aKG0Xj1Jd1dmXk7RjDhP9qlD4-XCAlQ4U2n0zSeLHIVBhsqRmvL2393miiWkmSMUiBADq1x-eKNguz71zevi6cc"

def to_sec(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

def to_str(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"

def get_result_from_data(data):
    stats = defaultdict(lambda: {"total": 0, "talk": 0})
    print(len(data['data']))
    for item in data.get("data", []):
        employees = item.get("employees", [])
        if not employees: continue
        name = employees[0].get("value", "").strip()
        if not name: continue
        total = item.get("call_total_duration", "00:00:00")
        talk = item.get("call_talk_duration", "00:00:00")
        stats[name]["total"] += to_sec(total)
        stats[name]["talk"] += to_sec(talk)
    return [
        {
            "name": name,
            "total_duration": to_str(values["total"]),
            "talk_duration": to_str(values["talk"]),
        }
        for name, values in stats.items()
    ]

def send_telegram_message(data):
    if not data:
        return False
    lines = ["📊 <b>Отчёт по звонкам</b>\n"]
    for i, item in enumerate(data, 1):
        lines.append(
            f"{i}. <b>{item['name']}</b>\n"
            f"   ⏱ Общее: {item['total_duration']}\n"
            f"   🎤 Разговор: {item['talk_duration']}\n"
        )
    text = "\n".join(lines)
    url = f"{TELEGRAM_DOMEN}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.status_code == 200
    except Exception as e:
        print("Ошибка:", e)
        return False

def send_report_calls(date = dt.today().strftime("%Y-%m-%d")):
    # print(get_token())
    response = requests.post( url_uis_report, headers=headers_uis,
        cookies={
            "app_id": "128603",
            "access_token": get_token(),
            }, json=generate_payload(date), timeout=60, )
    data = response.json()
    result = get_result_from_data(data)
    return send_telegram_message(result) 