import uuid

from apex.models import *
from apex.db_dump import dump


print('Loading profiles')
for profile in dump['Profile']:
    new_user = None

    if 'user' in profile:
        user = next(item for item in dump['User'] if item['uid'] == profile['user'])
        
        new_user = User.objects.create(username=user['username'], password=user['password'])

    else:
        new_username = uuid.uuid4().hex + '@infrabel.be'
        new_password = uuid.uuid4().hex

        new_user = User.objects.create(username=new_username, password=new_password)


    if 'user' in profile: del profile['user']

    new_profile = Profile.objects.create(**profile)
    new_profile.user = new_user
    new_profile.save()


print('Loading circles')
for circle in dump['Circle']:
    Circle.objects.create(**circle)


print('Loading teams')
for team in dump['Team']:
    circle = Circle.objects.get(uid=team['circle'])
    team['circle'] = circle

    if Team.objects.filter(name=team['name']).count() == 0:
        Team.objects.create(**team)


print('Loading apps')
for app in dump['App']:
    team = Team.objects.get(uid=app['team'])
    app['team'] = team

    App.objects.create(**app)


print('Creating Planner apps')
for team in Team.objects.all():
    app, c = App.objects.get_or_create(
        app='planner',
        team=team,
    )

    folder = Folder.objects.create(name="1", color="light-blue")
    AppFolderLink.objects.create(app=app, folder=folder, position=0)


print('Loading team profile links')
for team_profile_link in dump['TeamProfileLink']:
    team = Team.objects.get(uid=team_profile_link['team'])
    team_profile_link['team'] = team

    profile = Profile.objects.get(uid=team_profile_link['profile'])
    team_profile_link['profile'] = profile

    if team_profile_link['watcher_color'] == 'red accent-4':
        team_profile_link['watcher_color'] = 'red'

    TeamProfileLink.objects.create(**team_profile_link)


print('Loading cells')
for cell in dump['Cell']:
    profile = Profile.objects.filter(uid=cell['profile']).first()

    if profile:
        cell['profile'] = profile

        Cell.objects.create(**cell)


print('Loading days')
for day in dump['Day']:
    app = App.objects.filter(uid=day['team']).first()

    if app:
        day['team'] = app.team

        Day.objects.create(**day)


print('Loading tasks')
for task in dump['Task']:
    Task.objects.create(**task)


print('Loading subtasks')
for subtask in dump['Subtask']:
    Subtask.objects.create(**subtask)


print('Loading inputs')
for _input in dump['Input']:
    Input.objects.create(**_input)


print('Loading notes')
for note in dump['Note']:
    profile = Profile.objects.filter(uid=note['profile']).first()
    note['profile'] = profile

    if profile:
        Note.objects.create(**note)


print('Loading calls')
for call in dump['Call']:
    Call.objects.create(**call)


print('Loading links')
for link in dump['Link']:
    Link.objects.create(**link)


print('Loading app task links')
for link in dump['AppTaskLink']:
    task = Task.objects.get(uid=link['task'])
    link['task'] = task

    app = App.objects.get(uid=link['app'])
    team = app.team
    planner = team.app_set.filter(app='planner').first()

    link['folder'] = planner.folders.first()
    del link['app']

    FolderTaskLink.objects.create(**link)


print('Loading day task links')
for link in dump['DayTaskLink']:
    task = Task.objects.get(uid=link['task'])
    link['task'] = task

    day = Day.objects.get(uid=link['day'])
    day.has_content = True
    day.save()
    link['day'] = day

    DayTaskLink.objects.create(**link)


print('Loading cell task links')
for link in dump['CellTaskLink']:
    task = Task.objects.get(uid=link['task'])
    link['task'] = task

    cell = Cell.objects.get(uid=link['cell'])
    cell.has_content = True
    cell.save()
    link['cell'] = cell

    CellTaskLink.objects.create(**link)


print('Loading cell call links')
for link in dump['CellCallLink']:
    call = Call.objects.get(uid=link['call'])
    link['call'] = call

    cell = Cell.objects.get(uid=link['cell'])
    cell.has_call = True
    cell.save()
    link['cell'] = cell

    CellCallLink.objects.create(**link)


print('Loading call link links')
for link in dump['CallLinkLink']:
    call = Call.objects.filter(uid=link['call']).first()
    link['call'] = call

    _link = Link.objects.filter(uid=link['link']).first()
    link['link'] = _link

    if call and link:
        CallLinkLink.objects.create(**link)


print('Loading task input links')
for link in dump['TaskInputLink']:
    task = Task.objects.filter(uid=link['task']).first()
    link['task'] = task

    _input = Input.objects.filter(uid=link['input']).first()
    link['input'] = _input

    if task and _input:
        TaskInputLink.objects.create(**link)


print('Loading task subtask links')
for link in dump['TaskSubtaskLink']:
    task = Task.objects.filter(uid=link['task']).first()
    link['task'] = task

    subtask = Subtask.objects.filter(uid=link['subtask']).first()
    link['subtask'] = subtask

    if task and subtask:
        TaskSubtaskLink.objects.create(**link)


print('Loading task note links')
for link in dump['TaskNoteLink']:
    task = Task.objects.filter(uid=link['task']).first()
    link['task'] = task

    note = Note.objects.filter(uid=link['note']).first()
    link['note'] = note

    if task and note:
        TaskNoteLink.objects.create(**link)


print('Loading works')
for work in dump['Work']:
    work['date'] = '{0}-{1}-01'.format(work['date'].split('-')[0], work['date'].split('-')[1])

    Work.objects.create(**work)


print('Loading app work links')
for link in dump['AppWorkLink']:
    work = Work.objects.filter(uid=link['work']).first()
    link['work'] = work

    app = App.objects.filter(uid=link['app']).first()
    link['app'] = app

    if work and app:
        if not AppWorkLink.objects.filter(app=app, work=work).first():
            AppWorkLink.objects.create(**link)


print('Loading work columns')
for item in dump['WorkColumn']:
    work = Work.objects.filter(uid=item['work']).first()
    item['work'] = work

    if work:
        WorkColumn.objects.create(**item)


print('Loading work rows')
for item in dump['WorkRow']:
    work_column = WorkColumn.objects.filter(uid=item['work_column_uid']).first()
    item['work_column'] = work_column
    del item['work_column_uid']

    if work_column:
        WorkRow.objects.create(**item)


print('Loading shifts')
for item in dump['Shift']:
    work = Work.objects.filter(uid=item['work']).first()
    item['work'] = work

    if work:
        Shift.objects.create(**item)


print('Loading parts')
for item in dump['Part']:
    team = Team.objects.get(uid=item['team'])
    item['team'] = team

    shift = Shift.objects.filter(uid=item['shift']).first()
    item['shift'] = shift

    if team and shift:
        Part.objects.create(**item)


print('Loading part profile links')
for item in dump['PartProfileLink']:
    part = Part.objects.get(uid=item['part'])
    item['part'] = part

    profile = Profile.objects.get(uid=item['profile'])
    item['profile'] = profile

    if part and profile:
        PartProfileLink.objects.create(**item)




print('Cleaning doubles')

days = Day.objects.all()

for day in days:
    search = Day.objects.filter(team=day.team, date=day.date)

    if search.count() > 1:
        print(search)
        search[0].delete()


cells = Cell.objects.all()

for cell in cells:
    search = Cell.objects.filter(profile=cell.profile, date=cell.date)

    if search.count() > 1:
        print(search)
        search[0].delete()