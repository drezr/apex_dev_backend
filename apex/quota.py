import datetime
import math
import re


def get_quota(db, quota, rr_list, do_log):
    log = {'cn': list(), 'jc': list(), 'cv': list(), 'ch': list(), 'rh': list(),
           'rr': list(), 'hs': list(), 'mm': list(), 'cc': list(), 'ai': list(),
           'ag': list(), 'bt': list(), 'abs': list()}


    leaves = ['cn', 'jc', 'cv', 'ch', 'rh', 'rr']
    absences = ['mm', 'cc', 'ai', 'ag', 'bt']


    def is_day_rr(date, rr_list):
        for rr in rr_list:
            if date.day == rr['day'] and \
               date.month == rr['month'] and \
               date.year == rr['year']:
                return True

        return False


    def add_value(cell, _type, quota, log, op):
        quota[_type] += op

        if do_log:
            new_cell = cell.copy()
            new_cell['value'] = op
            log[_type].append(new_cell)

            if _type in absences:
                log['abs'].append(new_cell)


    def add_leaves(cell, p, pre, types, quota, log, op):
        for _type in types:
            if pre + _type in p:
                if 'p' in p:
                    quota['hp'] = quota['hp'] - 4 if pre else quota['hp'] - 8

                p = p.replace(pre + _type, '')

                add_value(cell, _type, quota, log, op)

        return p


    def get_cell(date, db, delta):
        next_date = date + datetime.timedelta(days=delta)

        for cell in db:
            if cell['day'] == next_date.day and \
               cell['month'] == next_date.month and \
               cell['year'] == next_date.year:

                return cell

        return None



    for cell in db:
        date = datetime.datetime(cell['year'], cell['month'], cell['day'])
        day_name = date.strftime('%A')

        if not cell['presence']: cell['presence'] = ''
        if not cell['absence']: cell['absence'] = ''

        p = cell['presence'].lower() + cell['absence'].lower()
        is_rr = is_day_rr(date, rr_list)

        p = p.replace('ap', '')
        p = p.replace(' ', '')

        hs = re.findall('[-|+][0-9]{1,}[\.*]{0,}[0-9]{0,}', p)

        # Remove hs
        for _hs in hs:
            p = p.replace(_hs, '')
            _hs = float(_hs)
            quota['hp'] += _hs

            add_value(cell, 'hs', quota, log, _hs)

        # Remove leaves, add absences
        if not ('ch' in p and day_name == 'Saturday') and \
           not ('rh' in p and day_name == 'Sunday') and \
           not ('rr' in p and is_rr):
            p = add_leaves(cell, p, '4', leaves, quota, log, -0.5)
            p = add_leaves(cell, p, '', leaves, quota, log, -1)
            
        p = add_leaves(cell, p, '4', absences, quota, log, 0.5)
        p = add_leaves(cell, p, '', absences, quota, log, 1)

        npn = re.search('[0-9]{0,}[p][n]', p)

        if npn:
            npn = npn.group(0)
            number = 8 if not npn.replace('pn', '') else int(npn.replace('pn', ''))
            p = p.replace(npn, '')
            quota['hp'] += number
            value = 0.5 if number <= 4 else 1

            if day_name in ['Saturday', 'Sunday']:
                if day_name == 'Saturday':
                    add_value(cell, 'ch', quota, log, value)

                elif day_name == 'Sunday':
                    add_value(cell, 'rh', quota, log, value)

            elif day_name not in ['Saturday', 'Sunday'] and is_rr:
                add_value(cell, 'rr', quota, log, value)


        np = re.search('[0-9]{0,}[p]', p)

        if np:
            np = np.group(0)
            number = 8 if not np.replace('p', '') else int(np.replace('p', ''))
            p = p.replace(np, '')
            quota['hp'] += number
            value = 0.5 if number <= 4 else 1

            if day_name in ['Saturday', 'Sunday']:
                if day_name == 'Saturday':
                    add_value(cell, 'ch', quota, log, value)

                if day_name == 'Sunday':
                    add_value(cell, 'rh', quota, log, value)

            elif day_name not in ['Saturday', 'Sunday'] and is_rr:
                add_value(cell, 'rr', quota, log, value)


        if '4oz' in p:
            p = p.replace('4oz', '')

            if day_name in ['Saturday', 'Sunday']:
                if day_name == 'Saturday':
                    add_value(cell, 'ch', quota, log, 0.5)

                if day_name == 'Sunday':
                    add_value(cell, 'rh', quota, log, 0.5)

            elif day_name not in ['Saturday', 'Sunday'] and is_rr:
                add_value(cell, 'rr', quota, log, 0.5)



    quota['abs'] = quota['mm'] + quota['cc'] + quota['ai'] + quota['ag'] + quota['bt']
    abs_no_bt = quota['mm'] + quota['cc'] + quota['ai'] + quota['ag']

    for i in range(math.floor(abs_no_bt / 28)):
        add_value({'month': 13}, 'jc', quota, log, -1)

    for i in range(math.floor(quota['abs'] / 28)):
        add_value({'month': 13}, 'cv', quota, log, -1)

    for key, val in quota.items():
        quota[key] = int(val) if isinstance(val, float) and val.is_integer() else val


    return quota, log