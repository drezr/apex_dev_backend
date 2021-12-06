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


def compute_quota(cells, quotas, config, holidays, detailed):

    leave_kinds = [
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

    excluded_leave_kinds = [
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

    credit_variable_kinds = {
        'credit': list(),
        'variable': list(),
    }

    codes = list()
    leave_types = list()
    sorted_leave_types = list()
    base_quotas = dict()
    computed_quotas = dict()
    detailed_quotas = dict()


    for quota in quotas:
        base_quotas[quota['code']] = float(quota['value'])
        computed_quotas[quota['code']] = float(quota['value'])
        detailed_quotas[quota['code']] = list()


    for leave_type in config['leave_types']:
        codes.append(leave_type['code'])

        leave_types.append({
            'code': leave_type['code'],
            'kind': leave_type['kind'],
        })

        if leave_type['code'] not in computed_quotas:
            computed_quotas[leave_type['code']] = 0
            detailed_quotas[leave_type['code']] = list()

        if leave_type['kind'] == 'credit_day':
            credit_variable_kinds['credit'].append(leave_type['code'])

        elif leave_type['kind'] == 'variable_leave':
            credit_variable_kinds['variable'].append(leave_type['code'])


    for leave_kind in leave_kinds:
        for leave_type in leave_types:
            if leave_type['kind'] == leave_kind:
                sorted_leave_types.append(leave_type)


    for cell in cells:
        cell_code = get_cell_code(cell)
        cell_date = get_cell_date(cell)
        day_name = cell_date.strftime('%A').lower()[0:3]
        cell_has_hour = None


        for leave_type in sorted_leave_types:
            kind = leave_type['kind']
            code = leave_type['code']

            if kind == 'hour':
                has_hs = re.findall('[-|+][0-9]{1,}[\.*]{0,}[0-9]{0,}', cell_code)

                for hs in has_hs:
                    cell['count'] = hs
                    computed_quotas[code] += float(hs)

                    if detailed:
                        detailed_quotas[code].append(cell)

                    cell_code = cell_code.replace(hs, '', 1)

            elif code in cell_code:
                amount = 0

                if kind not in excluded_leave_kinds:
                    has_hour = re.search('[0-9](' + code + ')', cell_code)
                    hour_count = 8 if not has_hour else has_hour.group(0).replace(code, '')
                    amount = 0.5 if int(hour_count) <= 4 else 1

                    is_normal = kind == 'normal_leave'
                    is_credit = kind == 'credit_day'
                    is_variable = kind == 'variable_leave'
                    is_counter = 'counter' in kind
                    is_recovery = kind == 'recovery'
                    is_presence = kind == 'presence'
                    is_sat = kind == 'saturday' and day_name == 'sat'
                    is_sun = kind == 'sunday' and day_name == 'sun'
                    is_holi = cell['date'] in holidays

                    if not is_sat and not is_sun and not is_holi and not is_recovery and not is_presence:
                        is_minus = (is_normal or is_credit or is_variable or not is_sat or not is_sun or not is_holi) and not is_counter

                        if has_hour:
                            amount = -amount if is_minus else amount

                        else:
                            amount = -amount if is_minus else amount

                        if is_counter:
                            counter_type = 'counter' if kind == 'counter' else kind.split('_')[1]

                            for key, val in counters_count.items():
                                if key == counter_type:
                                    counters_count[key] += 1

                            if counter_type not in ['counter']:
                                counters_count['total'] += 1

                                if counter_type != 'wounded':
                                    counters_count['total_no_wounded'] += 1

                        computed_quotas[code] += amount
                        
                        if detailed:
                            cell['count'] = '+' + str(amount) if amount > 0 else amount
                            detailed_quotas[code].append(cell)


                    if is_recovery or is_presence:
                        _kind = None

                        if day_name == 'sat': _kind = 'saturday'
                        elif day_name == 'sun': _kind = 'sunday'
                        elif is_holi: _kind = 'holiday'

                        if _kind:
                            for _leave_type in sorted_leave_types:
                                if _leave_type['kind'] == _kind:
                                    computed_quotas[_leave_type['code']] += amount
                                    
                                    if detailed:
                                        cell['count'] = '+' + str(amount)
                                        detailed_quotas[_leave_type['code']].append(cell)
                                

                if has_hour:
                    cell_code = cell_code.replace(has_hour.group(0), '')

                else:
                    cell_code = cell_code.replace(code, '')


    for key, val in computed_quotas.items():
        base_quotas[key] = int(val) if isinstance(val, float) and val.is_integer() else round(val, 2)
        computed_quotas[key] = int(val) if isinstance(val, float) and val.is_integer() else round(val, 2)


    for total, _kind in zip(['total', 'total_no_wounded'], ['variable', 'credit']):
        for i in range(math.floor(counters_count[total] / 28)):
            for _code in credit_variable_kinds[_kind]:
                computed_quotas[_code] -= 1

                if detailed:
                    detailed_quotas[_code].append({
                        'date': None,
                        'count': -1,
                    })


    return base_quotas, computed_quotas, detailed_quotas