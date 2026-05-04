import sys
from datetime import datetime
# from exelWork import send_telegram_exel
from phone_otchet import send_report_calls
from textWork import send_telegram_text
from tokenWork import refresh_token

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
    send_report_calls()
