import uuid

from django.db.models import Q

from shared.models import *
from watcher.models import *

models = ['User', 'App', 'AppContactLink', 'AppFolderLink', 'AppProjectLink', 'AppTaskLink', 'AppTemplateLink', 'AppWorkLink', 'Call', 'CallFileLink', 'CallLinkLink', 'Cell', 'CellCallLink', 'CellFileLink', 'CellNoteLink', 'CellTaskLink', 'Circle', 'Day', 'DayFileLink', 'DayNoteLink', 'DayTaskLink', 'File', 'Folder', 'FolderFileLink', 'FolderLinkLink', 'FolderNoteLink', 'FolderTaskLink', 'Holiday', 'Input', 'LeaveConfig', 'LeaveType', 'Link', 'Log', 'Message', 'Note', 'Part', 'PartProfileLink', 'Profile', 'Project', 'ProjectTaskLink', 'Quota', 'RadiumConfig', 'RadiumConfigColumn', 'Shift', 'Subtask', 'Task', 'TaskFileLink', 'TaskInputLink', 'TaskLinkLink', 'TaskNoteLink', 'TaskSubtaskLink', 'Team', 'TeamProfileLink', 'User', 'Work', 'WorkColumn', 'WorkFileLink', 'WorkRow']

dump = dict()

for model in models:
    dump[model] = list()


def convert_date(year, month, day):
    if not year or not month or not day:
        return None

    return '{0}-{1}-{2}'.format(str(year), str(month) if month > 9 else '0' + str(month), str(day) if day > 9 else '0' + str(day))



# DELETE BEFORE 2022 STUFF

# for unit_type in ['work', 'day', 'cell', 'work_participation', 'work_shift']:
#     units = Unit.objects.filter(type=unit_type, year__lt=2022)
#     units_count = units.count()

#     for i, unit in enumerate(units):
#         print('Deleting {0} #{1} ({2}/{3})'.format(unit_type, unit.id, i, units_count))
#         unit.delete()


# leaves = Leaves.objects.filter(year__lt=2022)
# leaves_count = leaves.count()

# for i, leave in enumerate(leaves):
#     print('Deleting {0} #{1} ({2}/{3})'.format('leave', leave.id, i, leaves_count))
#     leave.delete()




# DUMP DATABASE

a_file = open("/mnt/c/Users/dumon/Desktop/new_db.py", "w")
a_file.truncate()
a_file.close()

f = open("/mnt/c/Users/dumon/Desktop/new_db.py", "a")


print('Fetching profiles and users')
profiles = Profile.objects.all()

for profile in profiles:
    if profile.name:
        data = {
            'id': profile.id,
            'name': profile.name,
            'phone': profile.phone,
            'ident': profile.identification,
            'grade': profile.grade,
            'field': profile.field,
        }

        if profile.user:
            data['user'] = profile.user.id

            dump['User'].append({
                'id': profile.user.id,
                'username': profile.user.username,
                'password': profile.user.password,
            })

        dump['Profile'].append(data)


print('Fetching team profile links')
units = ProfileLink.objects.filter(Q(is_participant=False) | Q(is_available=False))

for unit in units:
    parent = unit.unit

    if parent.type == 'circle' and parent.app == 'watcher' and unit.profile.name:
        if unit.is_manager:
            dump['TeamProfileLink'].append({
                'profile': unit.profile.id,
                'team': parent.main_parent.id,
                'watcher_color': unit.color,
                'position': unit.position,
                'is_manager': True,
                'planner_is_editor': True,
                'planner_is_user': True,
                'draft_is_editor': True,
                'draft_is_user': True,
                'draft_can_see_private': True,
                'radium_is_editor': True,
                'watcher_is_editor': True,
                'watcher_is_user': True,
                'watcher_is_visible': True,
                'watcher_is_printable': True,
                'watcher_can_see_cells': True,
                'watcher_can_see_quotas': True,
            })

        else:
            dump['TeamProfileLink'].append({
                'profile': unit.profile.id,
                'team': parent.main_parent.id,
                'watcher_color': unit.color,
                'position': unit.position,
            })


print('Fetching circles')
units = Unit.objects.filter(type='circle', app='apex')
dump['Circle'] = [{'id': unit.id, 'name': unit.name} for unit in units if unit.id != 1]


print('Fetching teams')
units = Unit.objects.filter(type='circle', app='hub')
dump['Team'] = [{'id': unit.id, 'name': unit.name, 'circle': unit.main_parent.id} for unit in units]


print('Fetching apps')
units = Unit.objects.filter(type='circle', app__in=['watcher', 'radium', 'draft'])
dump['App'] = [{'id': unit.id, 'name': unit.value, 'team': unit.main_parent.id, 'app': unit.app} for unit in units if unit.main_parent]


print('Fetching works')
units = Unit.objects.filter(type='work')

work_old_columns = [
    'description',
    'expand.note',
    'extension',
    'expand.upm',
    'status',
    'expand.zkl',
    'expand.cat',
    'expand.grue',
    'expand.osv',
    'expand.loco',
    'expand.hgs',
    'expand.soud',
    'expand.pn',
    'expand.art',
    'expand.s428',
    'expand.s461',
    'expand.atwtx',
    'expand.imputation',
    'expand.sidenote',
    'expand.scst',
]

work_new_columns = {
    'scst': 'supervisor',
    'sidenote': 'extra',
    'imputation': 'imputation',
    'atwtx': 'atwtx',
    's461': 's461',
    's428': 's428',
    'art': 'art',
    'pn': 'pn',
    'soud': 'soudure',
    'hgs': 'hgs',
    'loco': 'loco',
    'osv': 'osv',
    'grue': 'grue',
    'cat': 'cascat',
    'zkl': 'zkl',
    'status': 'status',
    'upm': 'upm',
    'extension': 'ilt',
    'note': 'note',
    'description': 'description',
}

for unit in units:
    links = UnitLink.objects.filter(child=unit)

    for link in links:
        if link:
            if link.is_original:
                date = convert_date(unit.year, unit.month, unit.day)

                if date:
                    dump['Work'].append({'id': unit.id, 'date': date, 'color': unit.color})

                    for work_old_column in work_old_columns:
                        expand = Expand.objects.filter(unit=unit).first()

                        if 'expand' in work_old_column:
                            if expand:
                                column_name = work_old_column.split('.')[1]
                                colmun_value = getattr(expand, column_name)

                                if colmun_value:
                                    dump['WorkColumn'].append({'uid': uuid.uuid4().hex, 'name': work_new_columns[column_name], 'value': colmun_value, 'work': unit.id})

                        else:
                            colmun_value = getattr(unit, work_old_column)

                            if colmun_value:
                                dump['WorkColumn'].append({'uid': uuid.uuid4().hex, 'name': work_new_columns[work_old_column], 'value': colmun_value, 'work': unit.id})

            parent = link.parent

            if parent.type == 'circle' and parent.app == 'radium':
                dump['AppWorkLink'].append({'app': parent.id, 'work': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching shifts, limits and s460s')
units = Unit.objects.filter(type__in=['work_shift', 'work_limit', 'work_s460'])

for unit in units:
    link = UnitLink.objects.filter(child=unit).first()

    if link:
        work = link.parent

        column_uid = uuid.uuid4().hex

        _type = unit.type.split('_')[1]

        dump['WorkColumn'].append({'uid': column_uid, 'name': _type + 's', 'value': None, 'work': work.id})

        if _type == 'shift':
            date = convert_date(unit.year, unit.month, unit.day)

            dump['Shift'].append({
                'date': date,
                'shift': unit.start,
                'position': link.position,
                'work': work.id,
            })

        elif _type == 'limit':
            dump['WorkRow'].append({
                'from_line': unit.name,
                'from_station': unit.absence,
                'from_signal': unit.info,
                'from_lane': unit.presence,
                'from_pk': unit.extra,
                'to_line': unit.value,
                'to_station': unit.end,
                'to_signal': unit.place,
                'to_lane': unit.start,
                'to_pk': unit.description,
                'position': link.position,
                'work_column_uid': column_uid,
            })

        elif _type == 's460':
            dump['WorkRow'].append({
                'from_lane': unit.value,
                'from_pk': unit.start,
                'to_pk': unit.end,
                'position': link.position,
                'work_column_uid': column_uid,
            })


print('Fetching parts')
units = Unit.objects.filter(type='work_participation')

for unit in units:
    app = Unit.objects.get(pk=unit.place)
    team = app.main_parent
    date = convert_date(unit.year, unit.month, unit.day)
    dump['Part'].append({'id': unit.id, 'needs': unit.value, 'team': team.id, 'locked': unit.protected, 'shift': unit.main_parent.id, 'date': date})


print('Fetching profile part links')
units = ProfileLink.objects.filter(Q(is_participant=True) | Q(is_available=True))

for unit in units:
    parent = unit.unit

    if parent.type == 'work_participation':
        dump['PartProfileLink'].append({'profile': unit.profile.id, 'part': parent.id, 'is_participant': unit.is_participant, 'is_available': unit.is_available})


print('Fetching days')
units = Unit.objects.filter(type='day')

for unit in units:
    date = convert_date(unit.year, unit.month, unit.day)

    if date:
        dump['Day'].append({'id': unit.id, 'date': date, 'team': unit.main_parent.id})


print('Fetching cells')
units = Unit.objects.filter(type='cell')

for unit in units:
    date = convert_date(unit.year, unit.month, unit.day)

    if date and unit.profile:
        dump['Cell'].append({'id': unit.id, 'presence': unit.presence, 'absence': unit.absence, 'short': unit.info, 'color': unit.color, 'date': date, 'profile': unit.profile.id})


print('Fetching tasks')
units = Unit.objects.filter(type='task')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Task'].append({'id': unit.id, 'name': unit.name, 'status': unit.status})
                found_is_original = True

            parent = link.parent

            if parent.type == 'circle' and parent.app == 'watcher':
                dump['AppTaskLink'].append({'day': parent.id, 'task': unit.id, 'is_original': link.is_original, 'position': link.position})

            elif parent.type == 'cell':
                dump['CellTaskLink'].append({'cell': parent.id, 'task': unit.id, 'is_original': link.is_original, 'position': link.position})

            elif parent.type == 'day':
                dump['DayTaskLink'].append({'day': parent.id, 'task': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching calls')
units = Unit.objects.filter(type='call')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Call'].append({'id': unit.id, 'name': unit.name, 'kind': unit.value, 'start': unit.start, 'end': unit.end, 'description': unit.description})
                found_is_original = True

            parent = link.parent

            dump['CellCallLink'].append({'cell': parent.id, 'call': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching links')
units = Unit.objects.filter(type='link')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Link'].append({'id': unit.id, 'name': unit.name, 'kind': unit.value, 'start': unit.start, 'end': unit.end, 'description': unit.description})
                found_is_original = True

            parent = link.parent

            if parent.type == 'call':
                dump['CallLinkLink'].append({'call': parent.id, 'link': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching subtask')
units = Unit.objects.filter(type='subtask')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Subtask'].append({'id': unit.id, 'name': unit.name, 'status': unit.status})
                found_is_original = True

            parent = link.parent

            if parent.type == 'task':
                dump['TaskSubtaskLink'].append({'task': parent.id, 'subtask': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching input')
units = Unit.objects.filter(type='field')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Input'].append({'id': unit.id, 'kind': unit.status, 'name': unit.name, 'value': unit.value})
                found_is_original = True

            parent = link.parent

            if parent.type == 'task':
                dump['TaskInputLink'].append({'task': parent.id, 'input': unit.id, 'is_original': link.is_original, 'position': link.position})


print('Fetching note')
units = Unit.objects.filter(type='note')

for unit in units:
    links = UnitLink.objects.filter(child=unit)
    found_is_original = False

    for link in links:
        if link:
            if link.is_original and not found_is_original:
                dump['Note'].append({'id': unit.id, 'value': unit.value, 'profile': unit.profile.id if unit.profile else None})
                found_is_original = True

            parent = link.parent

            if parent.type == 'task':
                dump['TaskNoteLink'].append({'task': parent.id, 'note': unit.id, 'is_original': link.is_original, 'position': link.position})







print('Writing data...')

f.write(str("dump = {\n" + "\n".join("\t{!r}: {!r},".format(k, v) for k, v in dump.items()) + "\n}"))

f.close()

print('Done.')