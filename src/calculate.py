from collections import defaultdict

import requests
from config import BASE_DOMAIN, CALL_SHORT_MAX, CALL_MEDIUM_MAX, UNIQUE_DIALOG_MIN_DURATION, NEW_LEAD_MAX_CALLS
from env import long_token

def extract_duration_and_contact(event):
    """Извлекает длительность и contact_id"""
    value_after = event.get('value_after')
    duration = 0
    contact_id = None
    if isinstance(value_after, dict):
        params = value_after.get('params', {})
        duration = params.get('duration', 0)
        contact_id = params.get('element_id')
        if not contact_id:
            contact_id = event.get('entity_id')
    return duration, contact_id

def calculate_lead_stats(events):
    """Рассчитывает статистику по лидам"""
    contact_stats = defaultdict(lambda: {
        'calls': 0, 'dialogs': 0,
        'unique_call_dates': set(),
        'soglasiye': False, 'doshlo': False,
        'lead_id':None
    })
    for event in events:
        event_type = event.get('type')
        if event_type in (17, 30):
            duration, contact_id = extract_duration_and_contact(event)
            if not contact_id:
                continue
            contact_stats[contact_id]['calls'] += 1
            if duration > 0:
                contact_stats[contact_id]['dialogs'] += 1
        elif event_type == 14:
            value_after = event.get('value_after')
            if value_after:
                after_id = value_after.get('status_id')
                contact_id = event.get('object', {}).get('id')
                if not contact_id:
                    continue
                if after_id == 79428030:
                    contact_stats[contact_id]['soglasiye'] = True
                elif after_id == 79428038:
                    contact_stats[contact_id]['doshlo'] = True
    return contact_stats

def return_headers_oma(long_token):
    return {   
        "Authorization": f"Bearer {long_token}", 
        "Content-Type": "application/json"
    }
def lead_had_oma_before(lead_id, id_event):
    r = requests.get(f"{BASE_DOMAIN}/api/v4/events", headers=return_headers_oma(long_token), params={"limit":100,"filter[entity]":"lead","filter[entity_id][]":lead_id}, timeout=30)
    items = r.json().get("_embedded", {}).get("events", [])
    oma_count = 0
    for ev in items:
        value_after = ev.get("value_after", [])
        if value_after:
            if value_after[0].get("lead_status", {}).get("id") == id_event:
                oma_count+=1
                if oma_count>1:return True
    return False

def calculate_stats_for_manager(events, contact_stats):
    """Рассчитывает статистику для менеджера"""
    stats = {
        'total_calls': 0, 'outgoing': 0, 'incoming': 0,
        'answered': 0, 'missed': 0,
        'short_calls': 0, 'medium_calls': 0, 'long_calls': 0,
        'dialogs_25s': 0, 'unique_contacts': set(),
        'oma': 0, 'soma': 0, 'soga': 0, 'oga': 0, 'ola':0, 'sola':0,
        'refusals': 0, 'refusals_after_trial': 0, 'thinking': 0,
        'cancel_after_first_payment':0, 'refusal_after_trial':0, 'failure_after_secondary':0,
        'new_leads': {'calls': 0, 'dialogs': 0, 'unique_dialogs': set(), 'contacts': set(), 'dialogs_25s': 0},
        'old_leads': {'calls': 0, 'dialogs': 0, 'unique_dialogs': set(), 'contacts': set(), 'dialogs_25s': 0},
        'payments_primary':{'oma': 0,'oga': 0,}, 
        'payments_repeat':{'oma': 0,'oga': 0,}, 
    }
    lead_category = {
        cid: 'new' if c['calls'] <= NEW_LEAD_MAX_CALLS else 'old'
        for cid, c in contact_stats.items()
    }
    for event in events:
        event_type = event.get('type')
        if event_type in (17, 30):
            duration, contact_id = extract_duration_and_contact(event)
            is_outgoing = (event_type == 30)
            stats['total_calls'] += 1
            if is_outgoing:
                stats['outgoing'] += 1
            else:
                stats['incoming'] += 1
            if duration > 0:
                stats['answered'] += 1
                if duration < CALL_SHORT_MAX:
                    stats['short_calls'] += 1
                elif duration < CALL_MEDIUM_MAX:
                    stats['medium_calls'] += 1
                else:
                    stats['long_calls'] += 1
                if duration >= UNIQUE_DIALOG_MIN_DURATION and contact_id:
                    stats['dialogs_25s'] += 1
                    stats['unique_contacts'].add(str(contact_id))
            else:
                stats['missed'] += 1
            if contact_id and contact_id in lead_category:
                category = lead_category[contact_id]
                if category == 'new':
                    stats['new_leads']['calls'] += 1
                    if duration > 0:
                        stats['new_leads']['dialogs'] += 1
                        if duration >= UNIQUE_DIALOG_MIN_DURATION:
                            stats['new_leads']['unique_dialogs'].add(str(contact_id))
                            stats['new_leads']['dialogs_25s'] += 1
                    stats['new_leads']['contacts'].add(str(contact_id))
                else:
                    stats['old_leads']['calls'] += 1
                    if duration > 0:
                        stats['old_leads']['dialogs'] += 1
                        if duration >= UNIQUE_DIALOG_MIN_DURATION:
                            stats['old_leads']['unique_dialogs'].add(str(contact_id))
                            stats['old_leads']['dialogs_25s'] += 1
                    stats['old_leads']['contacts'].add(str(contact_id))
        elif event_type == 14:
            value_after = event.get('value_after')
            if value_after:
                after_id = value_after.get('status_id')
                if after_id == 79428378:
                    stats['oma'] += 1
                    if lead_had_oma_before(event.get("object", {}).get("id"), 79428378):
                        stats['payments_repeat']['oma'] += 1
                    else:
                        stats['payments_primary']['oma'] += 1
                elif after_id == 79428382:
                    if lead_had_oma_before(event.get("object", {}).get("id"), 79428382):
                        stats['payments_repeat']['oga'] += 1
                    else:
                        stats['payments_primary']['oga'] += 1
                elif after_id == 79428042: 
                    stats['soma'] += 1
                elif after_id == 79428374: 
                    stats['soga'] += 1
                elif after_id == 86052682: 
                    stats['ola'] += 1
                elif after_id == 86052686: 
                    stats['sola'] += 1   
                elif after_id == 79428394:
                    stats['refusals'] += 1
                elif after_id == 79428390:
                    stats['thinking'] += 1
                elif after_id == 84757154:
                    stats["cancel_after_first_payment"] += 1
                elif after_id == 84056278:
                    stats["refusal_after_trial"] += 1
    new_calls = stats['new_leads']['calls']
    old_calls = stats['old_leads']['calls']
    new_dialogs = stats['new_leads']['dialogs']
    old_dialogs = stats['old_leads']['dialogs']
    stats['new_leads']['conversion_to_dialogs'] = round(new_dialogs / new_calls * 100, 1) if new_calls > 0 else 0
    stats['old_leads']['conversion_to_dialogs'] = round(old_dialogs / old_calls * 100, 1) if old_calls > 0 else 0
    new_unique = len(stats['new_leads']['unique_dialogs'])
    old_unique = len(stats['old_leads']['unique_dialogs'])
    stats['new_leads']['conversion_from_dialogs'] = round(new_unique / new_dialogs * 100, 1) if new_dialogs > 0 else 0
    stats['old_leads']['conversion_from_dialogs'] = round(old_unique / old_dialogs * 100, 1) if old_dialogs > 0 else 0
    stats['new_leads']['unique_dialogs_count'] = new_unique
    stats['old_leads']['unique_dialogs_count'] = old_unique
    return stats

def calculate_stats_for_telemarketer(events, contact_stats):
    """Рассчитывает статистику для телемаркетолога"""
    stats = {
        'total_calls': 0, 'outgoing': 0, 'incoming': 0,
        'answered': 0, 'missed': 0,
        'short_calls': 0, 'medium_calls': 0, 'long_calls': 0,
        'dialogs_25s': 0, 'unique_contacts': set(),
        'refusals': 0, 'thinking': 0,
        'soglasiy_na_probnoe': 0, 'doshlo_do_probnika': 0,
        'perezapis_1': 0, 'perezapis_2': 0,
        'added_group_contacts': set(),
        'new_leads': {'calls': 0, 'dialogs': 0, 'unique_dialogs': set(), 'contacts': set(),
                      'soglasiye': 0, 'doshlo': 0, 'dialogs_25s': 0},
        'old_leads': {'calls': 0, 'dialogs': 0, 'unique_dialogs': set(), 'contacts': set(),
                      'soglasiye': 0, 'doshlo': 0, 'dialogs_25s': 0},
    }
    lead_category = {}
    seen_people = set()
    for contact_id, cstats in contact_stats.items():
        total_calls = cstats['calls']
        lead_category[contact_id] = 'new' if total_calls <= NEW_LEAD_MAX_CALLS else 'old'
    for event in events:
        event_type = event.get('type')
        if event_type in (17, 30):
            duration, contact_id = extract_duration_and_contact(event)
            is_outgoing = (event_type == 30)
            stats['total_calls'] += 1
            if is_outgoing:
                stats['outgoing'] += 1
            else:
                stats['incoming'] += 1
            if duration > 0:
                stats['answered'] += 1
                if duration < CALL_SHORT_MAX:
                    stats['short_calls'] += 1
                elif duration < CALL_MEDIUM_MAX:
                    stats['medium_calls'] += 1
                else:
                    stats['long_calls'] += 1
                if duration >= UNIQUE_DIALOG_MIN_DURATION and contact_id:
                    stats['dialogs_25s'] += 1
                    stats['unique_contacts'].add(str(contact_id))
            else:
                stats['missed'] += 1
            if contact_id and contact_id in lead_category:
                category = lead_category[contact_id]
                if category == 'new':
                    stats['new_leads']['calls'] += 1
                    if duration > 0:
                        stats['new_leads']['dialogs'] += 1
                        if duration >= UNIQUE_DIALOG_MIN_DURATION:
                            stats['new_leads']['unique_dialogs'].add(str(contact_id))
                            stats['new_leads']['dialogs_25s'] += 1
                    stats['new_leads']['contacts'].add(str(contact_id))
                else:
                    stats['old_leads']['calls'] += 1
                    if duration > 0:
                        stats['old_leads']['dialogs'] += 1
                        if duration >= UNIQUE_DIALOG_MIN_DURATION:
                            stats['old_leads']['unique_dialogs'].add(str(contact_id))
                            stats['old_leads']['dialogs_25s'] += 1
                    stats['old_leads']['contacts'].add(str(contact_id))
        elif event_type == 14:
            value_after = event.get('value_after')
            if value_after:
                after_id = value_after.get('status_id')
                contact_id = event.get('object', {}).get('id')
                if after_id == 79428394:
                    stats['refusals'] += 1
                elif after_id == 79428390:
                    stats['thinking'] += 1
                elif after_id == 79428030:
                    if contact_id not in seen_people:
                        seen_people.add(contact_id)
                        stats['soglasiy_na_probnoe'] += 1
                    else:
                        print("gg")
                    # stats['soglasiy_na_probnoe'] += 1
                    if contact_id and contact_id in lead_category:
                        if lead_category[contact_id] == 'new':
                            stats['new_leads']['soglasiye'] += 1
                        else:
                            stats['old_leads']['soglasiye'] += 1
                elif after_id == 79428038:
                    stats['doshlo_do_probnika'] += 1
                    if contact_id and contact_id in lead_category:
                        if lead_category[contact_id] == 'new':
                            stats['new_leads']['doshlo'] += 1
                        else:
                            stats['old_leads']['doshlo'] += 1
                elif after_id == 80982754:
                    stats['perezapis_1'] += 1
                elif after_id == 80982758:
                    stats['perezapis_2'] += 1
                elif after_id == 79428034:
                    lead_id = event.get('object', {}).get('id')
                    if lead_id:
                        stats['added_group_contacts'].add(lead_id)
                    contact_id = event.get('object', {}).get('id')
                    if contact_id:
                        contact_id = int(contact_id)
                        stats['added_group_contacts'].add(contact_id)
    # --- НОВЫЕ ---
    new_calls = stats['new_leads']['calls']
    new_dialogs = stats['new_leads']['dialogs']
    new_sogl = stats['new_leads']['soglasiye']
    new_doshlo = stats['new_leads']['doshlo']
    stats['new_leads']['unique_dialogs_count'] = len(stats['new_leads']['unique_dialogs'])
    # --- СТАРЫЕ ---
    old_calls = stats['old_leads']['calls']
    old_dialogs = stats['old_leads']['dialogs']
    old_sogl = stats['old_leads']['soglasiye']
    old_doshlo = stats['old_leads']['doshlo']
    stats['old_leads']['unique_dialogs_count'] = len(stats['old_leads']['unique_dialogs'])
    # --- КОНВЕРСИИ НОВЫЕ ---
    try:
        stats['new_leads']['conv_soglasie_to_dialog'] = round(new_sogl / stats['new_leads']['unique_dialogs_count']  * 100, 1) if new_calls else 0
    except ZeroDivisionError:
        stats['new_leads']['conv_soglasie_to_dialog'] = 0
    stats['new_leads']['conv_dialog_to_sogl'] = round(new_sogl / new_dialogs * 100, 1) if new_dialogs else 0
    stats['new_leads']['conv_dialog_to_doshlo'] = round(new_doshlo / new_dialogs * 100, 1) if new_dialogs else 0
    stats['new_leads']['conv_sogl_to_doshlo'] = round(new_doshlo / new_sogl * 100, 1) if new_sogl else 0
    # --- КОНВЕРСИИ СТАРЫЕ ---
    try:
        stats['old_leads']['conv_soglasie_to_dialog'] = round(old_sogl / stats['old_leads']['unique_dialogs_count'] * 100, 1) if old_calls else 0
    except ZeroDivisionError:
        stats['old_leads']['conv_soglasie_to_dialog'] = 0
    stats['old_leads']['conv_dialog_to_sogl'] = round(old_sogl / old_dialogs * 100, 1) if old_dialogs else 0
    stats['old_leads']['conv_dialog_to_doshlo'] = round(old_doshlo / old_dialogs * 100, 1) if old_dialogs else 0
    stats['old_leads']['conv_sogl_to_doshlo'] = round(old_doshlo / old_sogl * 100, 1) if old_sogl else 0
    # --- ОБЩИЕ ---
    total_calls = stats['total_calls']
    total_dialogs = stats['answered']
    total_sogl = stats['soglasiy_na_probnoe']
    total_doshlo = stats['doshlo_do_probnika']

    stats['conv_call_to_dialog'] = round(total_dialogs / total_calls * 100, 1) if total_calls else 0
    stats['conv_dialog_to_sogl'] = round(total_sogl / total_dialogs * 100, 1) if total_dialogs else 0
    stats['conv_dialog_to_doshlo'] = round(total_doshlo / total_dialogs * 100, 1) if total_dialogs else 0
    stats['conv_sogl_to_doshlo'] = round(total_doshlo / total_sogl * 100, 1) if total_sogl else 0

    stats['added_group'] = len(stats['added_group_contacts'])
    return stats

