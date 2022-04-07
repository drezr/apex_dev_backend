from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    ident = models.CharField(max_length=100, null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    field = models.CharField(max_length=100, null=True, blank=True)
    
    can_see_calendars = models.BooleanField(default=False)

    pref_planner_simplified = models.BooleanField(default=False)

    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='profile',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Circle(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Circle #{0}] {1}'.format(self.id, self.name)


class Team(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    circle = models.ForeignKey('Circle', on_delete=models.CASCADE)
    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='TeamProfileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Team #{0}] {1}'.format(self.id, self.name)


class App(models.Model):

    app = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, blank=True, null=True)

    template = models.ForeignKey('Task', related_name='template', on_delete=models.SET_NULL, blank=True, null=True)
    
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='AppTaskLink',
    )
    
    contacts = models.ManyToManyField(
        'Profile',
        blank=True,
        through='AppContactLink',
        related_name='contact'
    )
    
    folders = models.ManyToManyField(
        'Folder',
        blank=True,
        through='AppFolderLink',
        related_name='folder'
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        name = None

        if self.team:
            name = 'Team : ' + self.team.name

        elif self.profile:
            name = 'Profile : ' + self.profile.name

        return '[App #{0}] {1} ({2})'.format(self.id, self.app, name)


class Day(models.Model):

    date = models.DateField()
    has_content = models.BooleanField(default=False)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='DayTaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        through='DayNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        through='DayFileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('date', 'team', )

    def __str__(self):
        return '[Day #{0}] {1} ({2})'.format(
            self.id, self.date, self.team.name)


class Cell(models.Model):

    date = models.DateField()
    presence = models.CharField(max_length=20, blank=True, null=True)
    absence = models.CharField(max_length=20, blank=True, null=True)
    short = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    presence_color = models.CharField(max_length=20, blank=True, null=True)
    absence_color = models.CharField(max_length=20, blank=True, null=True)
    has_content = models.BooleanField(default=False)
    has_call = models.BooleanField(default=False)

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='CellTaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        through='CellNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        through='CellFileLink',
    )
    calls = models.ManyToManyField(
        'Call',
        blank=True,
        through='CellCallLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('date', 'profile', )

    def __str__(self):
        return '[Cell #{0}] {1} ({2})'.format(
            self.id, self.date, self.profile.name)


class Work(models.Model):

    color = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateField()

    apps = models.ManyToManyField(
        'App',
        blank=True,
        through='AppWorkLink',
    )

    files = models.ManyToManyField(
        'File',
        blank=True,
        through='WorkFileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        desc = ''

        for column in self.columns.all():
            if column.name == 'description' and column.value:
                desc = column.value[:15]
                break

        return '[Work #{0}] {1}'.format(self.id, desc)


class WorkColumn(models.Model):

    name = models.CharField(max_length=150)
    value = models.TextField(null=True, blank=True)
    bg_color = models.CharField(max_length=20, blank=True, null=True)
    text_color = models.CharField(max_length=20, blank=True, null=True)
    is_edited = models.BooleanField(default=False)

    work = models.ForeignKey(
        'Work', related_name='columns', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'work', )

    def __str__(self):
        return '[WorkColumn #{0}] {1} : {2} ({3})'.format(
            self.id, self.name, self.value, self.work)


class WorkRow(models.Model):

    from_line = models.TextField(blank=True, null=True)
    to_line = models.TextField(blank=True, null=True)

    from_station = models.TextField(blank=True, null=True)
    to_station = models.TextField(blank=True, null=True)

    from_signal = models.TextField(blank=True, null=True)
    to_signal = models.TextField(blank=True, null=True)

    from_lane = models.TextField(blank=True, null=True)
    to_lane = models.TextField(blank=True, null=True)

    from_pk = models.TextField(blank=True, null=True)
    to_pk = models.TextField(blank=True, null=True)

    from_date = models.TextField(blank=True, null=True)
    to_date = models.TextField(blank=True, null=True)

    from_hour = models.TextField(blank=True, null=True)
    to_hour = models.TextField(blank=True, null=True)

    zone = models.TextField(blank=True, null=True)
    subzone = models.TextField(blank=True, null=True)

    kind = models.TextField(blank=True, null=True)
    
    bg_color = models.CharField(max_length=20, blank=True, null=True)
    text_color = models.CharField(max_length=20, blank=True, null=True)

    position = models.PositiveSmallIntegerField()

    work_column = models.ForeignKey(
        'WorkColumn', related_name='rows', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[WorkRow #{0}] from ({1})'.format(self.id, self.work_column)


class Shift(models.Model):

    date = models.DateField(null=True, blank=True)
    shift = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Shift #{0}] {1} | {2}'.format(self.id, self.date, self.shift)


class Part(models.Model):

    date = models.DateField()
    needs = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    locked = models.BooleanField(default=False)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)
    project = models.ForeignKey(
        'Project', null=True, blank=True, on_delete=models.SET_NULL)

    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='PartProfileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('team', 'shift', )

    def __str__(self):
        return '[Part #{0}] {1} [{2}] [{3}]'.format(
            self.id, self.team.name, self.date, self.shift.work)


class Project(models.Model):

    name = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    private = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    apps = models.ManyToManyField(
        'App',
        blank=True,
        through='AppProjectLink',
    )
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='ProjectTaskLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Project #{0}] {1}'.format(self.id, self.name)


class Folder(models.Model):

    name = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=40, blank=True, null=True)

    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='FolderTaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        through='FolderNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        through='FolderFileLink',
    )
    links = models.ManyToManyField(
        'Link',
        blank=True,
        through='FolderLinkLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Folder #{0}] {1}'.format(self.id, self.name)


class Task(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    subtasks = models.ManyToManyField(
        'Subtask',
        blank=True,
        through='TaskSubtaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        through='TaskNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        through='TaskFileLink',
    )
    inputs = models.ManyToManyField(
        'Input',
        blank=True,
        through='TaskInputLink',
    )
    links = models.ManyToManyField(
        'Link',
        blank=True,
        through='TaskLinkLink',
    )
    codes = models.ManyToManyField(
        'Code',
        blank=True,
        through='TaskCodeLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Task #{0}] {1}'.format(self.id, self.name)


class Subtask(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Subtask #{0}] {1}'.format(self.id, self.name)


class Note(models.Model):

    value = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    profile = models.ForeignKey(
        'Profile', on_delete=models.SET_NULL, null=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Note #{0}] {1}'.format(self.id, self.value)


class File(models.Model):

    kind = models.CharField(max_length=100, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    extension = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[File #{0}] {1}.{2}'.format(self.id, self.name, self.extension)


class Input(models.Model):

    kind = models.CharField(max_length=100, blank=True, null=True)
    key = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    heading = models.BooleanField(default=False)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Input #{0}] {1} : {2}'.format(self.id, self.key, self.value)


class Link(models.Model):

    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Link #{0}] {1} : {2}'.format(self.id, self.name, self.url)


class Code(models.Model):

    presence = models.CharField(max_length=30, null=True, blank=True, default='0080')
    hour = models.PositiveSmallIntegerField(null=True, blank=True)
    start = models.CharField(max_length=30, null=True, blank=True, default='00:00')
    end = models.CharField(max_length=30, null=True, blank=True, default='00:00')
    work = models.CharField(max_length=30, null=True, blank=True)
    place = models.CharField(max_length=30, null=True, blank=True)
    project = models.CharField(max_length=30, null=True, blank=True)
    other = models.CharField(max_length=30, null=True, blank=True)
    network = models.CharField(max_length=30, null=True, blank=True)
    activity = models.CharField(max_length=30, null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Code #{0}]'.format(self.id)


class Call(models.Model):

    name = models.TextField(null=True, blank=True)
    kind = models.TextField(null=True, blank=True)
    start = models.TextField(null=True, blank=True)
    end = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    files = models.ManyToManyField(
        'File',
        blank=True,
        through='CallFileLink',
    )

    links = models.ManyToManyField(
        'Link',
        blank=True,
        through='CallLinkLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Call #{0}] {1}'.format(self.id, self.name)


class Holiday(models.Model):

    date = models.DateField()

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Holiday #{0}] {1}'.format(self.id, self.date)


class Log(models.Model):

    field = models.CharField(max_length=255, blank=True, null=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    profile = models.ForeignKey('Profile', null=True, on_delete=models.SET_NULL)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)
    cell = models.ForeignKey('Cell', null=True, blank=True, on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Log #{0}] {1} : {2}'.format(self.id, self.field, self.profile.name)


class Message(models.Model):

    priority = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    author = models.ForeignKey('Profile', null=True, on_delete=models.CASCADE, related_name='author')
    profile = models.ForeignKey('Profile', null=True, blank=True, on_delete=models.CASCADE)
    app = models.ForeignKey('App', null=True, blank=True, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[Message #{0}] {1}'.format(self.id, self.message)


class Quota(models.Model):

    code = models.CharField(max_length=50, null=True, blank=True)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    year = models.PositiveSmallIntegerField()

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('code', 'profile', 'year', )

    def __str__(self):
        return '[Quota #{0}] [{1}] {2} : {3}'.format(
            self.id,
            self.profile,
            self.code if not self.code else self.code.upper(),
            self.year,
        )


class LeaveConfig(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[LeaveConfig #{0}] {1}'.format(self.id, self.app)


class LeaveType(models.Model):

    code = models.CharField(max_length=10)
    desc = models.CharField(max_length=50, blank=True, null=True)
    kind = models.CharField(max_length=20, default='normal_leave')
    color = models.CharField(max_length=20, default='red')
    position = models.PositiveSmallIntegerField()
    visible = models.BooleanField(default=False)

    config = models.ForeignKey(
        'LeaveConfig', related_name='leave_type_set', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('code', 'config', )

    def __str__(self):
        return '[LeaveType #{0}] {1} : {2}'.format(
            self.id, self.config, self.code)


class RadiumConfig(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[RadiumConfig #{0}] {1}'.format(self.id, self.app)


class RadiumConfigColumn(models.Model):

    name = models.CharField(max_length=50)
    position = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    textsize = models.PositiveSmallIntegerField()
    visible = models.BooleanField(default=True)
    multiple = models.BooleanField(default=False)
    clickable = models.BooleanField(default=False)
    path = models.CharField(max_length=255, blank=True, null=True)

    config = models.ForeignKey(
        'RadiumConfig', related_name='column_set', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '[RadiumConfigColumn #{0}] {1} : {2}'.format(
            self.id, self.config, self.name)


#######################################################
######################## Links ########################
#######################################################


class TeamProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    is_manager = models.BooleanField(default=False)

    planner_is_editor = models.BooleanField(default=False)
    planner_is_user = models.BooleanField(default=False)

    draft_is_editor = models.BooleanField(default=False)
    draft_is_user = models.BooleanField(default=False)
    draft_can_see_private = models.BooleanField(default=False)

    radium_is_editor = models.BooleanField(default=False)

    watcher_is_editor = models.BooleanField(default=False)
    watcher_is_user = models.BooleanField(default=False)
    watcher_is_visible = models.BooleanField(default=False)
    watcher_is_printable = models.BooleanField(default=False)
    watcher_can_see_cells = models.BooleanField(default=False)
    watcher_can_see_quotas = models.BooleanField(default=False)
    watcher_color = models.CharField(max_length=20, blank=True, null=True)
    watcher_border_color = models.CharField(max_length=20, blank=True, null=True)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'team', )

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.team.name)


class AppWorkLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'work', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.work)


class AppProjectLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'project', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.project)


class AppTaskLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'task', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.task)


class AppContactLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    contact = models.ForeignKey('Profile', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'contact', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.contact)


class AppFolderLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'folder', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.folder)


class AppTemplateLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    template = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('app', 'template', )

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.template)


class DayTaskLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('day', 'task', )

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.task)


class DayNoteLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('day', 'note', )

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.note)


class DayFileLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('day', 'file', )

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.file)


class CellTaskLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('cell', 'task', )

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.task)


class CellNoteLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('cell', 'note', )

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.note)


class CellFileLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('cell', 'file', )

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.file)


class CellCallLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    call = models.ForeignKey('Call', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('cell', 'call', )

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.call)


class CallFileLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('call', 'file', )
    
    def __str__(self):
        return '{0} : {1}'.format(self.call, self.file)


class CallLinkLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('call', 'link', )

    def __str__(self):
        return '{0} : {1}'.format(self.call, self.link)


class WorkFileLink(models.Model):

    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('work', 'file', )

    def __str__(self):
        return '{0} : {1}'.format(self.work, self.file)


class PartProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    part = models.ForeignKey('Part', on_delete=models.CASCADE)

    is_participant = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'part', )

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.part)


class ProjectTaskLink(models.Model):

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('project', 'task', )

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.task)


class TaskSubtaskLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    subtask = models.ForeignKey('Subtask', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'subtask', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.subtask)


class TaskNoteLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'note', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.note)


class TaskFileLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'file', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.file)


class TaskInputLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'input', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.input)


class TaskLinkLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'link', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.link)


class TaskCodeLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    code = models.ForeignKey('Code', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('task', 'code', )

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.code)


class FolderTaskLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('folder', 'task', )

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.task)


class FolderNoteLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('folder', 'note', )

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.note)


class FolderFileLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('folder', 'file', )

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.file)


class FolderLinkLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('folder', 'link', )

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.link)