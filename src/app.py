import sys
import time
import requests
from datetime import datetime
from data import TELEMARKETERS, MANAGERS
# from exelWork import build_report_excel, send_telegram_file, format_manager_report_exel, format_telemarketer_report_exel, BASE_DATA, os
from config import headers, TELEGRAM_BOT_TOKEN, TELEGRAM_DOMEN, TELEGRAM_CHAT_ID
from tokenWork import refresh_token, load_token
from formating import format_manager_report, format_telemarketer_report
from calculate import calculate_stats_for_manager, calculate_stats_for_telemarketer, calculate_lead_stats


def send_telegram_message(text):
    """Отправляет сообщение в Telegram"""
    if not text:
        return True
    
    MAX_LEN = 4000
    if len(text) <= MAX_LEN:
        url = f"{TELEGRAM_DOMEN}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                print(f"    ✅ Сообщение отправлено")
                return True
            else:
                print(f"    ❌ Ошибка: {response.status_code}")
                return False
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return False
    else:
        parts = []
        lines = text.split('\n')
        current_part = []
        current_len = 0
        for line in lines:
            if current_len + len(line) + 1 > MAX_LEN:
                parts.append('\n'.join(current_part))
                current_part = [line]
                current_len = len(line)
            else:
                current_part.append(line)
                current_len += len(line) + 1
        if current_part:
            parts.append('\n'.join(current_part))
        success = True
        for i, part in enumerate(parts):
            url = f"{TELEGRAM_DOMEN}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': f"📄 Часть {i+1}/{len(parts)}\n\n{part}",
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            try:
                response = requests.post(url, json=payload, timeout=30)
                if response.status_code != 200:
                    success = False
                time.sleep(0.5)
            except Exception as e:
                success = False
        if success:
            print(f"    ✅ Сообщение отправлено ({len(parts)} частей)")
        return success

def load_events_for_user(user_id, date_from, date_to, max_pages=20):
    """Загружает все события для пользователя"""
    all_events = []
    page = 1
    access_token = load_token()
    while page <= max_pages:
        data = {
            'filter[main_user][]': user_id,
            'filter_date_from': date_from,
            'filter_date_to': date_to,
            'useFilter': 'y',
            'page': page,
            'rows': 200,
        }
        try:
            response = requests.post(
                'https://makebeatschool.amocrm.ru/ajax/events/list/',
                cookies={"access_token":access_token},
                headers=headers,
                data=data,
                timeout=30
            )
            if response.status_code != 200:
                break
            result = response.json()
            events = result.get('response', {}).get('items', [])
            if not events:
                break
            all_events.extend(events)
            pagination = result.get('response', {}).get('pagination', {})
            has_next = pagination.get('has_next_page', 0)
            if not has_next:
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            break
    return all_events

def extractionDate(args):
    args = sys.argv[1:]
    if len(args) == 0:
        today = datetime.now()
        date_from = today.strftime("%d.%m.%Y")
        date_to = date_from
    elif len(args) == 1:
        d = datetime.strptime(args[0], "%Y-%m-%d")
        date_from = d.strftime("%d.%m.%Y")
        date_to = date_from
    elif len(args) == 2:
        d1 = datetime.strptime(args[0], "%Y-%m-%d")
        d2 = datetime.strptime(args[1], "%Y-%m-%d")
        date_from = d1.strftime("%d.%m.%Y")
        date_to = d2.strftime("%d.%m.%Y")
    else:
        raise ValueError( "Использование: python script.py [ГГГГ-ММ-ДД] "
            "или [ГГГГ-ММ-ДД ГГГГ-ММ-ДД]" )
    return date_from, date_to

def send_report(date_from, date_to, date_range, employers, calul_func, format_func, sent, failed):
    for emp in employers:
        user_id = emp['id']
        user_name = emp['name']
        print(f"  📌 {user_name}...")
        events = load_events_for_user(user_id, date_from, date_to, max_pages=10)
        if not events:
            print(f"    ⚠️ Нет событий, пропускаем")
            failed += 1
            continue
        contact_stats = calculate_lead_stats(events)
        stats = calul_func(events, contact_stats)
        report = format_func(stats, user_name, date_range)
        print(f"    📨 Отправка в Telegram...")
        if send_telegram_message(report): sent += 1
        else: failed += 1
        time.sleep(1)
    return sent, failed
def send_telegram_text(date_from, date_to, date_range):
    print(f"\n{'='*60}")
    print(f"📊 ОТЧЁТ ЗА {date_range}")
    print(f"📨 Отправка в Telegram...")
    print(f"{'='*60}\n")
    print("👔 МЕНЕДЖЕРЫ:")
    # send_manager_report(date_from, date_to, date_range)
    sent, failed =send_report(date_from, date_to, date_range, MANAGERS, 
                calculate_stats_for_manager, format_manager_report, 0, 0)
    print("\n📞 ТЕЛЕМАРКЕТОЛОГИ:")
    sent, failed =send_report(date_from, date_to, date_range, TELEMARKETERS, 
                calculate_stats_for_telemarketer, format_telemarketer_report, sent, failed)
    # send_telemarketolog_report(date_from, date_to, date_range)
    print(f"\n{'='*60}")
    print(f"✅ Отправлено: {sent}")
    print(f"❌ Не отправлено: {failed}")
    print(f"{'='*60}\n")

def main():
    args = sys.argv[1:]
    try:
        date_from, date_to = extractionDate(args)
    except ValueError as e:
        print(e)
        return
    date_range = f"{date_from} - {date_to}" if date_from != date_to else date_from
    send_telegram_text(date_from, date_to, date_range)
    # send_telegram_exel(date_from, date_to, date_range)

if __name__ == "__main__":
    # get_tokens()
    refresh_token()
    main()
