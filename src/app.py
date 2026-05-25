import sys
from datetime import datetime
# from exelWork import send_telegram_exel
from phone_otchet import send_report_calls
from textWork import send_telegram_text
# from tokenWork import refresh_token

def extractionDate():
    args = sys.argv[1:]
    if len(args) == 0:
        today = datetime.now()
        date_from = today.strftime("%d.%m.%Y")
        date_to = date_from
        date_from_iso = today.strftime("%Y-%m-%d")
        # date_to_iso = date_from_iso
    elif len(args) == 1:
        d = datetime.strptime(args[0], "%Y-%m-%d")
        date_from = d.strftime("%d.%m.%Y")
        date_to = date_from
        date_from_iso = d.strftime("%Y-%m-%d")
        # date_to_iso = date_from_iso
    elif len(args) == 2:
        d1 = datetime.strptime(args[0], "%Y-%m-%d")
        d2 = datetime.strptime(args[1], "%Y-%m-%d")
        date_from = d1.strftime("%d.%m.%Y")
        date_to = d2.strftime("%d.%m.%Y")
        date_from_iso = d1.strftime("%Y-%m-%d")
        # date_to_iso = d2.strftime("%Y-%m-%d")
    else:
        raise ValueError( "Использование: python script.py [ГГГГ-ММ-ДД] " "или [ГГГГ-ММ-ДД ГГГГ-ММ-ДД]")
    return date_from, date_to, date_from_iso

def main():
    try:
        date_from, date_to, date_from_iso = extractionDate()
    except ValueError as e:
        print(e)
        return
    date_range = f"{date_from} - {date_to}" if date_from != date_to else date_from
    send_telegram_text(date_from, date_to, date_range)
    send_report_calls(date_from_iso)
    # send_telegram_exel(date_from, date_to, date_range)

if __name__ == "__main__":
    main()
