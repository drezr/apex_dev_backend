import datetime
import math
import re


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

                    if name and 'type_' + str(i) not in detail:
                        result['type_' + str(i)] = 0
                        detail['type_' + str(i)] = list()
                        new_quota['type_' + str(i)] = float(quota['type_' + str(i)])

                        types_sorted[t].append({
                            'name': name,
                            'generic': 'type_' + str(i),
                            'type': config['leave_' + str(i) + '_type'],
                        })

    return result, new_quota, detail, types_sorted


def compute_quota(cells, quota, config, holidays, detailed):
    # Order matter !
    leave_types = [
        'ignore',
        'counter',
        'counter_sick',
        'counter_special',
        'counter_unjustified',
        'counter_strike',
        'counter_wounded',
        'normal_leave',
        'credit_day',
        'variable_leave',
        'saturday',
        'sunday',
        'holiday',
        'recovery',
        'presence',
        'hour',
    ]

    excluded_leave_types = [
        'ignore',
        'hour',
    ]

    counters_count = {
        'sick': 0,
        'special': 0,
        'unjustified': 0,
        'strike': 0,
        'wounded': 0,
        'total': 0,
        'total_no_wounded': 0,
    }

    credit_variable_types = {
        'credit': list(),
        'variable': list(),
    }

    result, quota, detail, types_sorted = get_types_data(
        config, leave_types, quota)

    for cell in cells:
        code = get_cell_code(cell)
        date = get_cell_date(cell)
        day_name = date.strftime('%A').lower()[0:3]
        has_hour = None

        for leave_type in leave_types:
            for type_detail in types_sorted[leave_type]:
                if type_detail['type'] == 'hour':
                    has_hs = re.findall('[-|+][0-9]{1,}[\.*]{0,}[0-9]{0,}', code)

                    for hs in has_hs:
                        cell['count'] = hs
                        quota[type_detail['generic']] += float(hs)

                        if detailed:
                            detail[type_detail['generic']].append(cell)

                        code = code.replace(hs, '', 1)


                elif type_detail['name'] in code:
                    amount = 0

                    if leave_type not in excluded_leave_types:
                        has_hour = re.search('[0-9](' + type_detail['generic'] + ')', code)
                        hour_count = 8 if not has_hour else has_hour.group(0).replace(type_detail['generic'], '')
                        amount = 0.5 if int(hour_count) <= 4 else 1

                        is_normal_type = type_detail['type'] == 'normal_leave'
                        is_credit_type = type_detail['type'] == 'credit_day'
                        is_variable_type = type_detail['type'] == 'variable_leave'
                        is_counter_type = 'counter' in type_detail['type']
                        is_recovery_type = type_detail['type'] == 'recovery'
                        is_presence_type = type_detail['type'] == 'presence'
                        is_sat = type_detail['type'] == 'saturday' and day_name == 'sat'
                        is_sun = type_detail['type'] == 'sunday' and day_name == 'sun'
                        is_holi = cell['date'] in holidays

                        if is_variable_type:
                            credit_variable_types['variable'].append(type_detail['generic'])

                        elif is_credit_type:
                            credit_variable_types['credit'].append(type_detail['generic'])

                        if not is_sat and not is_sun and not is_holi and not is_recovery_type and not is_presence_type:
                            is_minus = (is_normal_type or is_credit_type or is_variable_type or not is_sat or not is_sun or not is_holi) and not is_counter_type

                            if has_hour:
                                amount = -amount if is_minus else amount

                            else:
                                amount = -amount if is_minus else amount

                            if is_counter_type:
                                t = type_detail['type']
                                counter_type = 'counter' if t == 'counter' else t.split('_')[1]

                                for key, val in counters_count.items():
                                    if key == counter_type:
                                        counters_count[key] += 1

                                if counter_type not in ['counter']:
                                    counters_count['total'] += 1

                                    if counter_type != 'wounded':
                                        counters_count['total_no_wounded'] += 1


                            quota[type_detail['generic']] += amount
                            
                            if detailed:
                                cell['count'] = '+' + str(amount) if amount > 0 else amount
                                detail[type_detail['generic']].append(cell)


                        if is_recovery_type or is_presence_type:
                            _type = None

                            if day_name == 'sat': _type = 'saturday'
                            elif day_name == 'sun': _type = 'sunday'
                            elif is_holi: _type = 'holiday'

                            if _type:
                                for _leave_type in types_sorted[_type]:
                                    quota[_leave_type['generic']] += amount
                                    
                                    if detailed:
                                        cell['count'] = '+' + str(amount)
                                        detail[_leave_type['generic']].append(cell)
                                    

                    if has_hour:
                        code = code.replace(has_hour.group(0), '')

                    else:
                        code = code.replace(type_detail['name'], '')



    for key, val in quota.items():
        quota[key] = int(val) if isinstance(val, float) and val.is_integer() else round(val, 2)


    for total, _type in zip(['total', 'total_no_wounded'], ['variable', 'credit']):
        for i in range(math.floor(counters_count[total] / 28)):
            for type_name in credit_variable_types[_type]:
                quota[type_name] -= 1

                if detailed:
                    detail[type_name].append({
                        'date': None,
                        'count': -1,
                    })


    return quota, detail


# cells = [
#     {
#         'date': '2021-10-04', # lundi // rr
#         'presence': '',
#         'absence': '',
#     },
#     {
#         'date': '2021-10-05', # mardi
#         'presence': 'p',
#         'absence': '',
#     },
#     {
#         'date': '2021-10-06', # mercredi
#         'presence': '+2+2.26',
#         'absence': '',
#     },
#     {
#         'date': '2021-10-07', # jeudi
#         'presence': '-4',
#         'absence': '',
#     },
#     {
#         'date': '2021-10-08', # vendredi
#         'presence': '',
#         'absence': None,
#     },
#     {
#         'date': '2021-10-09', # samedi
#         'presence': '',
#         'absence': None,
#     },
#     {
#         'date': '2021-10-10', # dimache
#         'presence': '',
#         'absence': None,
#     },
# ]

# config = {
#     'id': 1,
#     'leave_count': 14,
#     'leave_0_name': 'P',
#     'leave_0_desc': 'Jours de présence',
#     'leave_0_type': 'presence',
#     'leave_0_color': 'green',
#     'leave_0_visible': False,
#     'leave_1_name': 'CN',
#     'leave_1_desc': 'Congés annuels',
#     'leave_1_type': 'day',
#     'leave_1_color': 'red',
#     'leave_1_visible': True,
#     'leave_2_name': 'JC',
#     'leave_2_desc': 'Jours de crédits',
#     'leave_2_type': 'day',
#     'leave_2_color': 'indigo',
#     'leave_2_visible': True,
#     'leave_3_name': 'CV',
#     'leave_3_desc': 'Jours compensatoires',
#     'leave_3_type': 'day',
#     'leave_3_color': 'yellow',
#     'leave_3_visible': True,
#     'leave_4_name': 'CH',
#     'leave_4_desc': 'Congé hebdomadaires',
#     'leave_4_type': 'saturday',
#     'leave_4_color': 'blue',
#     'leave_4_visible': True,
#     'leave_5_name': 'RH',
#     'leave_5_desc': 'Repos hebdomadaires',
#     'leave_5_type': 'sunday',
#     'leave_5_color': 'pink',
#     'leave_5_visible': True,
#     'leave_6_name': 'RR',
#     'leave_6_desc': 'Jours fériés',
#     'leave_6_type': 'holiday',
#     'leave_6_color': 'orange',
#     'leave_6_visible': True,
#     'leave_7_name': 'HS',
#     'leave_7_desc': 'Heures supplémentaire',
#     'leave_7_type': 'hour',
#     'leave_7_color': 'green',
#     'leave_7_visible': True,
#     'leave_8_name': 'MM',
#     'leave_8_desc': 'Jours de maladies',
#     'leave_8_type': 'counter',
#     'leave_8_color': 'purple',
#     'leave_8_visible': False,
#     'leave_9_name': 'CC',
#     'leave_9_desc': 'Congés de circonstances',
#     'leave_9_type': 'counter',
#     'leave_9_color': 'purple',
#     'leave_9_visible': False,
#     'leave_10_name': 'AI',
#     'leave_10_desc': 'Absences injustifiées',
#     'leave_10_type': 'counter',
#     'leave_10_color': 'purple',
#     'leave_10_visible': False,
#     'leave_11_name': 'AG',
#     'leave_11_desc': 'Agent en grève',
#     'leave_11_type': 'counter',
#     'leave_11_color': 'purple',
#     'leave_11_visible': False,
#     'leave_12_name': 'BT',
#     'leave_12_desc': 'Blessé au travail',
#     'leave_12_type': 'counter',
#     'leave_12_color': 'purple',
#     'leave_12_visible': False,
#     'leave_13_name': 'OZ',
#     'leave_13_desc': 'Récupération',
#     'leave_13_type': 'recovery',
#     'leave_13_color': 'red',
#     'leave_13_visible': False,
#     'leave_14_name': 'AP',
#     'leave_14_desc': 'Temps partiel',
#     'leave_14_type': 'ignore',
#     'leave_14_color': 'red',
#     'leave_14_visible': False,
#     'leave_15_name': None,
#     'leave_15_desc': None,
#     'leave_15_type': 'day',
#     'leave_15_color': 'red',
#     'leave_15_visible': False,
#     'leave_16_name': None,
#     'leave_16_desc': None,
#     'leave_16_type': 'day',
#     'leave_16_color': 'red',
#     'leave_16_visible': False,
#     'leave_17_name': None,
#     'leave_17_desc': None,
#     'leave_17_type': 'day',
#     'leave_17_color': 'red',
#     'leave_17_visible': False,
#     'leave_18_name': None,
#     'leave_18_desc': None,
#     'leave_18_type': 'day',
#     'leave_18_color': 'red',
#     'leave_18_visible': False,
#     'leave_19_name': None,
#     'leave_19_desc': None,
#     'leave_19_type': 'day',
#     'leave_19_color': 'red',
#     'leave_19_visible': False,
#     'app': 1
# }

# quota = {
#     'id': 1,
#     'year': 2021,
#     'type_0': 0,
#     'type_1': 0,
#     'type_2': 0,
#     'type_3': 0,
#     'type_4': 0,
#     'type_5': 0,
#     'type_6': 0,
#     'type_7': 0,
#     'type_8': 0,
#     'type_9': 0,
#     'type_10': 0,
#     'type_11': 0,
#     'type_12': 0,
#     'type_13': 0,
#     'type_14': 0,
#     'type_15': 0,
#     'type_16': 0,
#     'type_17': 0,
#     'type_18': 0,
#     'type_19': 0,
#     'profile': 1
# }

# holidays = [
#     '2021-10-04',
# ]



# result, detail = compute_quota(
#     cells=cells,
#     quota=quota,
#     config=config,
#     holidays=holidays,
#     detailed=True
# )


# print()
# print(result)
# print()
# print(detail)
