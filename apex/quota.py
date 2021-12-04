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
                        has_hour = re.search('[0-9](' + type_detail['name'] + ')', code)
                        hour_count = 8 if not has_hour else has_hour.group(0).replace(type_detail['name'], '')
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