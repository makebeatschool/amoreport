import time
import requests
from config import headers, long_token
# from tokenWork import load_token


def load_events_for_user(user_id, date_from, date_to, max_pages=20):
    """Загружает все события для пользователя"""
    all_events = []
    page = 1
    # access_token = load_token()
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
                cookies={"access_token":long_token},
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
