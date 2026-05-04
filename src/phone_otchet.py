from collections import defaultdict
import time
import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from collections import defaultdict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_DOMEN

start_date = "04.05.26"
end_date = "04.05.26"
login = "makebeatschool@gmail.com"
password = "J8wdnRDa"

def to_sec(t):
    h, m, s = map(int, t.split(":"))
    return h*3600 + m*60 + s
def to_str(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"

def open_site(login, password, date=None):
    # Даты пока не используем, как и в исходном коде
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://go.uiscom.ru/login", wait_until="domcontentloaded")
    page.locator('input[name="login"]').fill(login)
    page.locator('input[name="password"]').fill(password)
    page.locator('button[type="submit"]').click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(8000)
    page.goto("https://go.uiscom.ru/reports/calls/2300492", wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    return p, browser, context, page

def get_result(login, password, date=None):
    p, browser, context, page = open_site(login, password, date)
    stats = defaultdict(lambda: {"total": 0, "talk": 0})
    try:
        while True:
            rows = page.locator("table tbody tr")
            row_count = rows.count()
            for i in range(row_count):
                try:
                    row = rows.nth(i)
                    tds = row.locator("td")
                    name = tds.nth(9).inner_text().strip()
                    total = tds.nth(11).inner_text().strip()
                    talk = tds.nth(12).inner_text().strip()
                    if not name: continue
                    stats[name]["total"] += to_sec(total)
                    stats[name]["talk"] += to_sec(talk)
                except Exception:
                    continue
            try:
                next_btn = page.locator('[test-id="pagination__next"]')
                if next_btn.get_attribute("disabled") is not None:
                    break
                next_btn.click()
                page.wait_for_timeout(2000)
            except PlaywrightTimeoutError: break
            except Exception: break
        return [
            {
                "name": name,
                "total_duration": to_str(v["total"]),
                "talk_duration": to_str(v["talk"]),
            }
            for name, v in stats.items()
        ]
    finally:
        context.close()
        browser.close()
        p.stop()

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

def send_report_calls():
    print("получение звонков")
    result = get_result(login, password)
    print("отправка звонков")
    send_telegram_message(result)




# def open_site(login, password, date):
#     #  дату пока не трогаем
#     driver = webdriver.Chrome()
#     driver.get("https://go.uiscom.ru/login")
#     wait = WebDriverWait(driver, 20)
#     loginField = wait.until( EC.presence_of_element_located((By.NAME, "login")))
#     loginField.clear()
#     loginField.send_keys(login)
#     passwordField = wait.until( EC.presence_of_element_located((By.NAME, "password")))
#     passwordField.clear()
#     passwordField.send_keys(password)
#     wait.until( EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
#     time.sleep(8) 
#     driver.get("https://go.uiscom.ru/reports/calls/2300492")
#     time.sleep(10)
#     return driver

# def get_result(login, password, start_date, end_date):
#     driver = open_site(login, password, start_date, end_date)
#     stats = defaultdict(lambda: {"total": 0, "talk": 0})
#     while True:
#         rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
#         for r in rows:
#             try:
#                 tds = r.find_elements(By.TAG_NAME, "td")
#                 name = tds[9].text.strip()
#                 total = tds[11].text.strip()
#                 talk = tds[12].text.strip()
#                 if not name:continue
#                 stats[name]["total"] += to_sec(total)
#                 stats[name]["talk"] += to_sec(talk)
#             except: continue
#         try:
#             next_btn = driver.find_element(By.CSS_SELECTOR, '[test-id="pagination__next"]')
#             if next_btn.get_attribute("disabled"):
#                 break
#             next_btn.click()
#             time.sleep(2)
#         except:
#             break

#     return [ {   "name":name,
#                 "total_duration": to_str(v["total"]), 
#                 "talk_duration": to_str(v["talk"]) 
#             } 
#          for name, v in stats.items()]