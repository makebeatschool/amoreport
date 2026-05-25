from datetime import datetime
import time
import requests
from amoCRMWork import load_events_for_user
from data import TELEMARKETERS, MANAGERS, MANAGERS23
from config import  TELEGRAM_DOMEN
from env import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from calculate import calculate_stats_for_manager, calculate_stats_for_telemarketer, calculate_lead_stats


def format_manager_report(stats, name, date_range):
    report = []
    report.append(f"👔 <b>{name}</b> (Менеджер)")
    report.append(f"📅 {date_range}")
    report.append("")
    report.append("📊 ОБЩАЯ СТАТИСТИКА")
    report.append(f"📞 Звонков: {stats['total_calls']}")
    report.append(f"📤 Исходящие: {stats['outgoing']}")
    report.append(f"📥 Входящие: {stats['incoming']}")
    report.append(f"💬 Диалоги: {stats['answered']}")
    report.append(f"🎯 Диалоги от 25 сек: {stats['dialogs_25s']}")
    report.append(f"🆔 Уникальные диалоги (≥25с): {len(stats['unique_contacts'])}")
    report.append(f"❌ Недозвон: {stats['missed']}")
    report.append("")
    report.append(f"🎯 ОМА: {stats['oma']}")
    report.append(f"🎯 СОМА: {stats['soma']}")
    report.append(f"🎯 СОГА: {stats['soga']}")
    report.append(f"🎯 ОГА: {stats['oga']}")
    report.append(f"🎯 ОЛА: {stats['ola']}")
    report.append(f"🎯 СОЛА: {stats['sola']}")
    report.append("")

    report.append("💰 ОПЛАТЫ")
    report.append("🟢 Первичные:")
    report.append(f"🎯  ОМА: {stats['payments_primary']['oma']}")
    report.append(f"🎯  ОГА:  {stats['payments_primary']['oga']}")
    report.append("🔴 Повторные:")
    report.append(f"🎯  ОМА: {stats['payments_repeat']['oma']}")
    report.append(f"🎯  ОГА: {stats['payments_repeat']['oga']}")

    report.append("")
    report.append(f"❌ Отказы: {stats['refusals']}")
    report.append(f"❌ Отказы после первой оплаты: {stats['cancel_after_first_payment']}")
    report.append(f"❌ Отказ после вторичного продления: {stats['failure_after_secondary']}")
    report.append(f"❌ Отказ после пробного: {stats['refusal_after_trial']}")
    report.append(f"⏳ Думают: {stats['thinking']}")
    report.append("")
    new = stats['new_leads']
    report.append("🟢 НОВЫЕ ЛИДЫ (≤3 звонков)")
    report.append(f"👥 Контактов: {len(new['contacts'])}")
    report.append(f"📞 Звонков: {new['calls']}")
    report.append(f"💬 Диалогов: {new['dialogs']}")
    report.append(f"🎯 Диалоги от 25 сек: {new['dialogs_25s']}")
    report.append(f"🆔 Уникальных: {new['unique_dialogs_count']}")
    report.append("")
    report.append(f"📈 Конверсия в дозвон: {new['conversion_to_dialogs']}%")
    report.append(f"📈 Конверсия диалогов: {new['conversion_from_dialogs']}%")
    report.append("")
    old = stats['old_leads']
    report.append("🔴 СТАРЫЕ ЛИДЫ (≥4 звонков)")
    report.append(f"👥 Контактов: {len(old['contacts'])}")
    report.append(f"📞 Звонков: {old['calls']}")
    report.append(f"💬 Диалогов: {old['dialogs']}")
    report.append(f"🎯 Диалоги от 25 сек: {old['dialogs_25s']}")
    report.append(f"🆔 Уникальных: {old['unique_dialogs_count']}")
    report.append("")
    report.append(f"📈 Конверсия в дозвон: {old['conversion_to_dialogs']}%")
    report.append(f"📈 Конверсия диалогов: {old['conversion_from_dialogs']}%")
    return '\n'.join(report)

def format_telemarketer_report(stats, name, date_range):
    report = []
    report.append(f"📞 <b>{name}</b> (ТМ)")
    report.append(f"📅 {date_range}")
    report.append("")
    report.append("📊 ОБЩАЯ СТАТИСТИКА")
    report.append(f"📞 Звонков: {stats['total_calls']}")
    report.append(f"📤 Исходящие: {stats['outgoing']}")
    report.append(f"📥 Входящие: {stats['incoming']}")
    report.append(f"💬 Диалоги: {stats['answered']}")
    report.append(f"🎯 Диалоги от 25 сек: {stats['dialogs_25s']}")
    report.append(f"🆔 Уникальные диалоги (≥25с): {len(stats['unique_contacts'])}")
    report.append(f"❌ Недозвон: {stats['missed']}")
    report.append("")
    report.append(f"❌ Отказы: {stats['refusals']}")
    report.append(f"⏳ Думают: {stats['thinking']}")
    report.append(f"✅ Согласие на пробное: {stats['soglasiy_na_probnoe']}")
    report.append(f"🎓 Дошло до пробника: {stats['doshlo_do_probnika']}")
    report.append(f"📝 Перезапись 1: {stats['perezapis_1']}")
    report.append(f"📝 Перезапись 2: {stats['perezapis_2']}")
    report.append("")
    new = stats['new_leads']
    report.append("🟢 НОВЫЕ ЛИДЫ (≤3 звонков)")
    report.append(f"👥 Контактов: {len(new['contacts'])}")
    report.append(f"📞 Звонков: {new['calls']}")
    report.append(f"💬 Диалогов: {new['dialogs']}")
    report.append(f"🎯 Диалоги от 25 сек: {new['dialogs_25s']}")
    report.append(f"🆔 Уникальных: {new['unique_dialogs_count']}")
    report.append(f"✅ Согласий: {new['soglasiye']}")
    report.append(f"🎓 Дошло до пробника: {new['doshlo']}")
    report.append("")
    report.append("🎯 РЕЗУЛЬТАТЫ")
    report.append(f"👥 Добавлены в группу: {len(stats['added_group_contacts'])}")
    report.append("")
    report.append(f"📈 Конверсия в согласие: {new['conv_soglasie_to_dialog']}%")
    report.append(f"📈 Конверсия в дозвон: {new['conv_dialog_to_sogl']}%")
    report.append(f"📈 Конверсия из диалогов в пробник: {new['conv_dialog_to_doshlo']}%")
    report.append(f"📈 Конверсия из согласия в пробник: {new['conv_sogl_to_doshlo']}%")
    report.append("")
    old = stats['old_leads']
    report.append("🔴 СТАРЫЕ ЛИДЫ (≥4 звонков)")
    report.append(f"👥 Контактов: {len(old['contacts'])}")
    report.append(f"📞 Звонков: {old['calls']}")
    report.append(f"💬 Диалогов: {old['dialogs']}")
    report.append(f"🎯 Диалоги от 25 сек: {old['dialogs_25s']}")
    report.append(f"🆔 Уникальных: {old['unique_dialogs_count']}")
    report.append(f"✅ Согласий: {old['soglasiye']}")
    report.append(f"🎓 Дошло до пробника: {old['doshlo']}")
    report.append("")
    report.append(f"📈 Конверсия в согласие: {old['conv_soglasie_to_dialog']}%")
    report.append(f"📈 Конверсия в дозвон: {old['conv_dialog_to_sogl']}%")
    report.append(f"📈 Конверсия из диалогов в пробник: {old['conv_dialog_to_doshlo']}%")
    report.append(f"📈 Конверсия из согласия в пробник: {old['conv_sogl_to_doshlo']}%")
    return '\n'.join(report)

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

    report_date = datetime.strptime(date_range, "%d.%m.%Y").date()
    today = datetime.now().date()
    current_hour = datetime.now().hour
    if report_date == today and current_hour >= 23:
        print("👔 МЕНЕДЖЕРЫ:")
        sent, failed = send_report(date_from, date_to, date_range, MANAGERS23,
                    calculate_stats_for_manager, format_manager_report, 0, 0)
    elif report_date == today:
        print("👔 МЕНЕДЖЕРЫ:")
        sent, failed = send_report(date_from, date_to, date_range, MANAGERS,
                    calculate_stats_for_manager, format_manager_report, 0, 0)
        print("\n📞 ТЕЛЕМАРКЕТОЛОГИ:")
        sent, failed = send_report(date_from, date_to, date_range, TELEMARKETERS,
                    calculate_stats_for_telemarketer, format_telemarketer_report, sent, failed)
    else:
        print("👔 МЕНЕДЖЕРЫ:")
        sent, failed = send_report(date_from, date_to, date_range, MANAGERS23,
                    calculate_stats_for_manager, format_manager_report, 0, 0)
        print("👔 МЕНЕДЖЕРЫ:")
        sent, failed = send_report(date_from, date_to, date_range, MANAGERS,
                    calculate_stats_for_manager, format_manager_report, sent, failed)
        print("\n📞 ТЕЛЕМАРКЕТОЛОГИ:")
        sent, failed = send_report(date_from, date_to, date_range, TELEMARKETERS,
                    calculate_stats_for_telemarketer, format_telemarketer_report, sent, failed)
    print(f"\n{'='*60}")
    print(f"✅ Отправлено: {sent}")
    print(f"❌ Не отправлено: {failed}")
    print(f"{'='*60}\n")
