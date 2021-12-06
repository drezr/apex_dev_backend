from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    ident = models.CharField(max_length=100, null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    field = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='profile')

    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='profile',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Circle(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='circle')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Team(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='team')

    circle = models.ForeignKey('Circle', on_delete=models.CASCADE)
    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='TeamProfileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class App(models.Model):

    app = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=50, editable=False, default='app')

    selected_template = models.ForeignKey('Template', on_delete=models.CASCADE, blank=True, null=True)
    
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='AppTaskLink',
    )
    
    files = models.ManyToManyField(
        'File',
        blank=True,
        through='AppFileLink',
    )
    
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        through='AppNoteLink',
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

    def __str__(self):
        name = None

        if self.team:
            name = 'Team : ' + self.team.name

        elif self.profile:
            name = 'Profile : ' + self.profile.name

        return '[#{0}] {1} ({2})'.format(self.id, self.app, name)


class Day(models.Model):

    date = models.DateField()
    has_content = models.BooleanField(default=False)
    type = models.CharField(max_length=50, editable=False, default='day')

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

    def __str__(self):
        return '[#{0}] {1} ({2})'.format(
            self.id, self.date, self.team.name)


class Cell(models.Model):

    date = models.DateField()
    presence = models.CharField(max_length=20, blank=True, null=True)
    absence = models.CharField(max_length=20, blank=True, null=True)
    short = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    has_content = models.BooleanField(default=False)
    has_call = models.BooleanField(default=False)
    type = models.CharField(max_length=50, editable=False, default='cell')

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

    def __str__(self):
        return '[#{0}] {1} ({2})'.format(
            self.id, self.date, self.profile.name)


class Work(models.Model):

    description = models.TextField(null=True, blank=True)
    description_bg_color = models.CharField(max_length=20, blank=True, null=True)
    description_is_edited = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    note_bg_color = models.CharField(max_length=20, blank=True, null=True)
    note_is_edited = models.BooleanField(default=False)
    ilt = models.TextField(null=True, blank=True)
    ilt_bg_color = models.CharField(max_length=20, blank=True, null=True)
    ilt_is_edited = models.BooleanField(default=False)
    upm = models.TextField(null=True, blank=True)
    upm_bg_color = models.CharField(max_length=20, blank=True, null=True)
    upm_is_edited = models.BooleanField(default=False)
    status = models.TextField(null=True, blank=True)
    status_bg_color = models.CharField(max_length=20, blank=True, null=True)
    status_is_edited = models.BooleanField(default=False)
    zkl = models.TextField(null=True, blank=True)
    zkl_bg_color = models.CharField(max_length=20, blank=True, null=True)
    zkl_is_edited = models.BooleanField(default=False)
    cascat = models.TextField(null=True, blank=True)
    cascat_bg_color = models.CharField(max_length=20, blank=True, null=True)
    cascat_is_edited = models.BooleanField(default=False)
    grue = models.TextField(null=True, blank=True)
    grue_bg_color = models.CharField(max_length=20, blank=True, null=True)
    grue_is_edited = models.BooleanField(default=False)
    osv = models.TextField(null=True, blank=True)
    osv_bg_color = models.CharField(max_length=20, blank=True, null=True)
    osv_is_edited = models.BooleanField(default=False)
    loco = models.TextField(null=True, blank=True)
    loco_bg_color = models.CharField(max_length=20, blank=True, null=True)
    loco_is_edited = models.BooleanField(default=False)
    hgs = models.TextField(null=True, blank=True)
    hgs_bg_color = models.CharField(max_length=20, blank=True, null=True)
    hgs_is_edited = models.BooleanField(default=False)
    soudure = models.TextField(null=True, blank=True)
    soudure_bg_color = models.CharField(max_length=20, blank=True, null=True)
    soudure_is_edited = models.BooleanField(default=False)
    pn = models.TextField(null=True, blank=True)
    pn_bg_color = models.CharField(max_length=20, blank=True, null=True)
    pn_is_edited = models.BooleanField(default=False)
    art = models.TextField(null=True, blank=True)
    art_bg_color = models.CharField(max_length=20, blank=True, null=True)
    art_is_edited = models.BooleanField(default=False)
    s428 = models.TextField(null=True, blank=True)
    s428_bg_color = models.CharField(max_length=20, blank=True, null=True)
    s428_is_edited = models.BooleanField(default=False)
    s461 = models.TextField(null=True, blank=True)
    s461_bg_color = models.CharField(max_length=20, blank=True, null=True)
    s461_is_edited = models.BooleanField(default=False)
    atwtx = models.TextField(null=True, blank=True)
    atwtx_bg_color = models.CharField(max_length=20, blank=True, null=True)
    atwtx_is_edited = models.BooleanField(default=False)
    imputation = models.TextField(null=True, blank=True)
    imputation_bg_color = models.CharField(max_length=20, blank=True, null=True)
    imputation_is_edited = models.BooleanField(default=False)
    extra = models.TextField(null=True, blank=True)
    extra_bg_color = models.CharField(max_length=20, blank=True, null=True)
    extra_is_edited = models.BooleanField(default=False)
    line = models.TextField(null=True, blank=True)
    line_bg_color = models.CharField(max_length=20, blank=True, null=True)
    line_is_edited = models.BooleanField(default=False)
    supervisor = models.TextField(null=True, blank=True)
    supervisor_bg_color = models.CharField(max_length=20, blank=True, null=True)
    supervisor_is_edited = models.BooleanField(default=False)
    colt = models.TextField(null=True, blank=True)
    colt_bg_color = models.CharField(max_length=20, blank=True, null=True)
    colt_is_edited = models.BooleanField(default=False)

    shifts_bg_color = models.CharField(max_length=20, blank=True, null=True)
    ilts_bg_color = models.CharField(max_length=20, blank=True, null=True)
    bnxs_bg_color = models.CharField(max_length=20, blank=True, null=True)
    fmhts_bg_color = models.CharField(max_length=20, blank=True, null=True)
    limits_bg_color = models.CharField(max_length=20, blank=True, null=True)
    s460s_bg_color = models.CharField(max_length=20, blank=True, null=True)

    color = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateField()
    type = models.CharField(max_length=50, editable=False, default='work')

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

    def __str__(self):
        desc = '' if not self.description else self.description[:10]
        return '[#{0}] {1}'.format(self.id, desc)


class Limit(models.Model):

    from_line = models.CharField(max_length=100, blank=True, null=True)
    from_station = models.CharField(max_length=100, blank=True, null=True)
    from_signal = models.CharField(max_length=100, blank=True, null=True)
    from_lane = models.CharField(max_length=100, blank=True, null=True)
    from_pk = models.CharField(max_length=100, blank=True, null=True)
    to_line = models.CharField(max_length=100, blank=True, null=True)
    to_station = models.CharField(max_length=100, blank=True, null=True)
    to_signal = models.CharField(max_length=100, blank=True, null=True)
    to_lane = models.CharField(max_length=100, blank=True, null=True)
    to_pk = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='limit')

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.work.description)


class S460(models.Model):

    line = models.CharField(max_length=100, blank=True, null=True)
    lane = models.CharField(max_length=100, blank=True, null=True)
    start = models.CharField(max_length=100, blank=True, null=True)
    end = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='s460')

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.work.description)


class Shift(models.Model):

    date = models.DateField(null=True, blank=True)
    shift = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='shift')

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} | {2}'.format(self.id, self.date, self.shift)


class Part(models.Model):

    date = models.DateField()
    needs = models.CharField(max_length=255, blank=True, null=True)
    locked = models.BooleanField(default=False)
    type = models.CharField(max_length=50, editable=False, default='part')

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    project = models.ForeignKey(
        'Project', null=True, blank=True, on_delete=models.SET_NULL)

    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='PartProfileLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} [{2}] [{3}]'.format(
            self.id, self.team.name, self.date, self.work.description)


class Project(models.Model):

    name = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    date = models.DateField()
    type = models.CharField(max_length=50, editable=False, default='project')

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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Template(models.Model):

    name = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='template')

    apps = models.ManyToManyField(
        'App',
        blank=True,
        through='AppTemplateLink',
    )
    inputs = models.ManyToManyField(
        'Input',
        blank=True,
        through='TemplateInputLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Folder(models.Model):

    name = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=40, blank=True, null=True)
    type = models.CharField(max_length=50, editable=False, default='folder')

    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='FolderTaskLink',
    )

    subtasks = models.ManyToManyField(
        'Subtask',
        blank=True,
        through='FolderSubtaskLink',
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
    inputs = models.ManyToManyField(
        'Input',
        blank=True,
        through='FolderInputLink',
    )
    links = models.ManyToManyField(
        'Link',
        blank=True,
        through='FolderLinkLink',
    )

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Task(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50, editable=False, default='task')

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

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Subtask(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50, editable=False, default='subtask')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Note(models.Model):

    value = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=50, editable=False, default='note')

    profile = models.ForeignKey(
        'Profile', on_delete=models.SET_NULL, null=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.value)


class File(models.Model):

    kind = models.CharField(max_length=100, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    extension = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='file')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}.{2}'.format(self.id, self.name, self.extension)


class Input(models.Model):

    kind = models.CharField(max_length=100, blank=True, null=True)
    key = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    heading = models.BooleanField(default=False)
    type = models.CharField(max_length=50, editable=False, default='input')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.key, self.value)


class Link(models.Model):

    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='link')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.name, self.url)


class Call(models.Model):

    name = models.TextField(null=True, blank=True)
    kind = models.TextField(null=True, blank=True)
    start = models.TextField(null=True, blank=True)
    end = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, editable=False, default='call')

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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Holiday(models.Model):

    date = models.DateField()
    type = models.CharField(max_length=50, editable=False, default='holiday')

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.date)


class Log(models.Model):

    field = models.CharField(max_length=255, blank=True, null=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, editable=False, default='log')

    profile = models.ForeignKey('Profile', null=True, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)
    cell = models.ForeignKey('Cell', null=True, blank=True, on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.field, self.profile.name)


class Message(models.Model):

    priority = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=50, editable=False, default='message')

    author = models.ForeignKey('Profile', null=True, on_delete=models.CASCADE, related_name='author')
    profile = models.ForeignKey('Profile', null=True, blank=True, on_delete=models.CASCADE)
    app = models.ForeignKey('App', null=True, blank=True, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.message)


class Quota(models.Model):

    code = models.CharField(max_length=50, null=True, blank=True)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    year = models.PositiveSmallIntegerField()

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] [{1}] {2} : {3}'.format(
            self.id,
            self.profile,
            self.code if not self.code else self.code.upper(),
            self.year,
        )


class LeaveConfig(models.Model):

    # Kind of an empty model. Might add more config options later.

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.app)


class LeaveType(models.Model):

    code = models.CharField(max_length=10, blank=True, null=True)
    desc = models.CharField(max_length=50, blank=True, null=True)
    kind = models.CharField(max_length=20, default='normal_leave')
    color = models.CharField(max_length=20, default='red')
    position = models.PositiveSmallIntegerField()
    visible = models.BooleanField(default=False)

    config = models.ForeignKey(
        'LeaveConfig', related_name='leave_type_set', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.config, self.code)


class RadiumConfig(models.Model):

    # Kind of an empty model. Might add more config options later.

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.app)


class RadiumConfigColumn(models.Model):

    name = models.CharField(max_length=50)
    position = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    textsize = models.PositiveSmallIntegerField()
    visible = models.BooleanField(default=True)

    config = models.ForeignKey(
        'RadiumConfig', related_name='column_set', on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.config, self.name)


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

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.team.name)


class AppWorkLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.work)


class AppProjectLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.project)


class AppTaskLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.task)


class AppFileLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.file)


class AppNoteLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.note)


class AppContactLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    contact = models.ForeignKey('Profile', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.contact)


class AppFolderLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.folder)


class DayTaskLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.task)


class DayNoteLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.note)


class DayFileLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.file)


class CellTaskLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.task)


class CellNoteLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.note)


class CellFileLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.file)


class CellCallLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    call = models.ForeignKey('Call', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.call)


class CallFileLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    
    def __str__(self):
        return '{0} : {1}'.format(self.call, self.file)


class CallLinkLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.call, self.link)


class WorkFileLink(models.Model):

    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.work, self.file)


class PartProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    part = models.ForeignKey('Part', on_delete=models.CASCADE)

    is_participant = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.part)


class ProjectTaskLink(models.Model):

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.task)


class AppTemplateLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    template = models.ForeignKey('Template', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.template)


class TemplateInputLink(models.Model):

    template = models.ForeignKey('Template', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.template, self.input)


class TaskSubtaskLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    subtask = models.ForeignKey('Subtask', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.subtask)


class TaskNoteLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.note)


class TaskFileLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.file)


class TaskInputLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.input)


class TaskLinkLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.link)


class FolderTaskLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.task)


class FolderSubtaskLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    subtask = models.ForeignKey('Subtask', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.subtask)


class FolderNoteLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.note)


class FolderFileLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.file)


class FolderInputLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.input)


class FolderLinkLink(models.Model):

    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{0} : {1}'.format(self.folder, self.link)