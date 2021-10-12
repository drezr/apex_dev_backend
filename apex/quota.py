import datetime
import re


cells = [
    {
        'date': '2021-10-04', # lundi // rr
        'presence': '',
        'absence': '',
    },
    {
        'date': '2021-10-05', # mardi
        'presence': '',
        'absence': '',
    },
    {
        'date': '2021-10-06', # mercredi
        'presence': '',
        'absence': '',
    },
    {
        'date': '2021-10-07', # jeudi
        'presence': '',
        'absence': '',
    },
    {
        'date': '2021-10-08', # vendredi
        'presence': '',
        'absence': None,
    },
    {
        'date': '2021-10-09', # samedi
        'presence': '4oz',
        'absence': None,
    },
    {
        'date': '2021-10-10', # dimache
        'presence': '',
        'absence': None,
    },
]

config = {
    'id': 1,
    'leave_count': 14,
    'leave_0_name': 'P',
    'leave_0_desc': 'Jours de présence',
    'leave_0_type': 'presence',
    'leave_0_color': 'green',
    'leave_0_visible': False,
    'leave_1_name': 'CN',
    'leave_1_desc': 'Congés annuels',
    'leave_1_type': 'day',
    'leave_1_color': 'red',
    'leave_1_visible': True,
    'leave_2_name': 'JC',
    'leave_2_desc': 'Jours de crédits',
    'leave_2_type': 'day',
    'leave_2_color': 'indigo',
    'leave_2_visible': True,
    'leave_3_name': 'CV',
    'leave_3_desc': 'Jours compensatoires',
    'leave_3_type': 'day',
    'leave_3_color': 'yellow',
    'leave_3_visible': True,
    'leave_4_name': 'CH',
    'leave_4_desc': 'Congé hebdomadaires',
    'leave_4_type': 'saturday',
    'leave_4_color': 'blue',
    'leave_4_visible': True,
    'leave_5_name': 'RH',
    'leave_5_desc': 'Repos hebdomadaires',
    'leave_5_type': 'sunday',
    'leave_5_color': 'pink',
    'leave_5_visible': True,
    'leave_6_name': 'RR',
    'leave_6_desc': 'Jours fériés',
    'leave_6_type': 'holiday',
    'leave_6_color': 'orange',
    'leave_6_visible': True,
    'leave_7_name': 'HS',
    'leave_7_desc': 'Heures supplémentaire',
    'leave_7_type': 'hour',
    'leave_7_color': 'green',
    'leave_7_visible': True,
    'leave_8_name': 'MM',
    'leave_8_desc': 'Jours de maladies',
    'leave_8_type': 'counter',
    'leave_8_color': 'purple',
    'leave_8_visible': False,
    'leave_9_name': 'CC',
    'leave_9_desc': 'Congés de circonstances',
    'leave_9_type': 'counter',
    'leave_9_color': 'purple',
    'leave_9_visible': False,
    'leave_10_name': 'AI',
    'leave_10_desc': 'Absences injustifiées',
    'leave_10_type': 'counter',
    'leave_10_color': 'purple',
    'leave_10_visible': False,
    'leave_11_name': 'AG',
    'leave_11_desc': 'Agent en grève',
    'leave_11_type': 'counter',
    'leave_11_color': 'purple',
    'leave_11_visible': False,
    'leave_12_name': 'BT',
    'leave_12_desc': 'Blessé au travail',
    'leave_12_type': 'counter',
    'leave_12_color': 'purple',
    'leave_12_visible': False,
    'leave_13_name': 'OZ',
    'leave_13_desc': 'Récupération',
    'leave_13_type': 'recovery',
    'leave_13_color': 'red',
    'leave_13_visible': False,
    'leave_14_name': 'AP',
    'leave_14_desc': 'Temps partiel',
    'leave_14_type': 'ignore',
    'leave_14_color': 'red',
    'leave_14_visible': False,
    'leave_15_name': None,
    'leave_15_desc': None,
    'leave_15_type': 'day',
    'leave_15_color': 'red',
    'leave_15_visible': False,
    'leave_16_name': None,
    'leave_16_desc': None,
    'leave_16_type': 'day',
    'leave_16_color': 'red',
    'leave_16_visible': False,
    'leave_17_name': None,
    'leave_17_desc': None,
    'leave_17_type': 'day',
    'leave_17_color': 'red',
    'leave_17_visible': False,
    'leave_18_name': None,
    'leave_18_desc': None,
    'leave_18_type': 'day',
    'leave_18_color': 'red',
    'leave_18_visible': False,
    'leave_19_name': None,
    'leave_19_desc': None,
    'leave_19_type': 'day',
    'leave_19_color': 'red',
    'leave_19_visible': False,
    'app': 1
}

quota = {
    'id': 1,
    'year': 2021,
    'type_0': 0,
    'type_1': 0,
    'type_2': 0,
    'type_3': 0,
    'type_4': 0,
    'type_5': 0,
    'type_6': 0,
    'type_7': 0,
    'type_8': 0,
    'type_9': 0,
    'type_10': 0,
    'type_11': 0,
    'type_12': 0,
    'type_13': 0,
    'type_14': 0,
    'type_15': 0,
    'type_16': 0,
    'type_17': 0,
    'type_18': 0,
    'type_19': 0,
    'profile': 1
}

holidays = [
    '2021-10-04',
]

# Order has importance !
leave_types = [
    'ignore', ####
    'counter', ####
    'day',
    'saturday',
    'sunday',
    'holiday',
    'recovery',
    'presence',
    'hour',
]

excluded_leave_types = [
    'ignore',
    'presence',
    'hour',
]

def get_cell_code(cell):
    pre = cell['presence']
    _abs = cell['absence']

    pre = '' if not pre else pre.lower()
    _abs = '' if not _abs else _abs.lower()

    return pre + '~~~~' + _abs


def get_cell_date(cell):
    year, month, day = cell['date'].split('-')

    return datetime.datetime(int(year), int(month), int(day))


def get_types_data(config, leave_types, quota):
    result = dict()
    detail = dict()
    types_sorted = dict()
    types_def = dict()
    new_quota = dict()

    for t in leave_types:
         types_sorted[t] = list()


    for item in config:
        if 'type' in item:
            i = item.split('_')[1]

            for t in leave_types:
                if config['leave_' + str(i) + '_type'] == t:
                    name = config['leave_' + str(i) + '_name']
                    name = None if not name else name.lower()

                    if name and name not in detail:
                        result[name] = 0
                        detail[name] = list()
                        types_def[name] = t
                        new_quota[name] = quota['type_' + str(i)]

                        types_sorted[t].append({
                            'name': name,
                            'type': config['leave_' + str(i) + '_type'],
                        })

    return result, new_quota, detail, types_sorted, types_def


def compute_quota(cells, quota, leave_types, config, holidays, detailed):
    result, quota, detail, types_sorted, types_def = get_types_data(config, leave_types, quota)

    for cell in cells:
        code = get_cell_code(cell)
        date = get_cell_date(cell)
        day_name = date.strftime('%A').lower()[0:3]
        has_hour = None

        for leave_type in leave_types:
            for type_detail in types_sorted[leave_type]:
                if type_detail['name'] in code:
                    amount = 0

                    if leave_type not in excluded_leave_types:
                        has_hour = re.search('[0-9](' + type_detail['name'] + ')', code)

                        is_day_type = type_detail['type'] == 'day'
                        is_counter_type = type_detail['type'] == 'counter'
                        is_recovery_type = type_detail['type'] == 'recovery'
                        is_sat = type_detail['type'] == 'saturday' and day_name == 'sat'
                        is_sun = type_detail['type'] == 'sunday' and day_name == 'sun'
                        is_holi = cell['date'] in holidays

                        is_minus = (is_day_type or not is_sat or not is_sun or not is_holi) and not is_counter_type

                        if not is_sat and not is_sun and not is_holi and not is_recovery_type:
                            if has_hour:
                                amount = -0.5 if is_minus else 0.5

                            else:
                                amount = -1 if is_minus else 1


                            quota[type_detail['name']] += amount
                            cell['count'] = '+' + amount if amount > 0 else amount
                            detail[type_detail['name']].append(cell)


                        if is_recovery_type:
                            if day_name == 'sat':
                                for sat_type in types_sorted['saturday']:
                                    if has_hour:
                                        quota[sat_type['name']] += 0.5
                                        cell['count'] = '+0.5'

                                    else:
                                        quota[sat_type['name']] += 1
                                        cell['count'] = '+1'
                                        
                                    detail[sat_type['name']].append(cell)
                                    

                    if has_hour:
                        code = code.replace(has_hour.group(0), '')

                    else:
                        code = code.replace(type_detail['name'], '')


    return quota, detail











result, detail = compute_quota(
    cells=cells,
    quota=quota,
    leave_types=leave_types,
    config=config,
    holidays=holidays,
    detailed=True
)


print()
print(result)
print()
print(detail)
