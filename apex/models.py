from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    ident = models.CharField(max_length=100, null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    field = models.CharField(max_length=100, null=True, blank=True)

    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='profile',
    )

    def __str__(self):
        return self.name


class Circle(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Team(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    circle = models.ForeignKey('Circle', on_delete=models.CASCADE)
    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='TeamProfileLink',
    )

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class App(models.Model):

    app = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        through='AppTaskLink',
    )

    def __str__(self):
        return '[#{0}] {1} ({2})'.format(self.id, self.app, self.team.name)


class RadiumSetting(models.Model):

    description_position = models.PositiveSmallIntegerField(null=True, blank=True)
    description_visible = models.BooleanField(default=False)
    note_position = models.PositiveSmallIntegerField(null=True, blank=True)
    note_visible = models.BooleanField(default=False)
    ilt_position = models.PositiveSmallIntegerField(null=True, blank=True)
    ilt_visible = models.BooleanField(default=False)
    upm_position = models.PositiveSmallIntegerField(null=True, blank=True)
    upm_visible = models.BooleanField(default=False)
    status_position = models.PositiveSmallIntegerField(null=True, blank=True)
    status_visible = models.BooleanField(default=False)
    zkl_position = models.PositiveSmallIntegerField(null=True, blank=True)
    zkl_visible = models.BooleanField(default=False)
    cascat_position = models.PositiveSmallIntegerField(null=True, blank=True)
    cascat_visible = models.BooleanField(default=False)
    grue_position = models.PositiveSmallIntegerField(null=True, blank=True)
    grue_visible = models.BooleanField(default=False)
    osv_position = models.PositiveSmallIntegerField(null=True, blank=True)
    osv_visible = models.BooleanField(default=False)
    loco_position = models.PositiveSmallIntegerField(null=True, blank=True)
    loco_visible = models.BooleanField(default=False)
    hgs_position = models.PositiveSmallIntegerField(null=True, blank=True)
    hgs_visible = models.BooleanField(default=False)
    soudure_position = models.PositiveSmallIntegerField(null=True, blank=True)
    soudure_visible = models.BooleanField(default=False)
    pn_position = models.PositiveSmallIntegerField(null=True, blank=True)
    pn_visible = models.BooleanField(default=False)
    art_position = models.PositiveSmallIntegerField(null=True, blank=True)
    art_visible = models.BooleanField(default=False)
    s428_position = models.PositiveSmallIntegerField(null=True, blank=True)
    s428_visible = models.BooleanField(default=False)
    s461_position = models.PositiveSmallIntegerField(null=True, blank=True)
    s461_visible = models.BooleanField(default=False)
    atwtx_position = models.PositiveSmallIntegerField(null=True, blank=True)
    atwtx_visible = models.BooleanField(default=False)
    imputation_position = models.PositiveSmallIntegerField(null=True, blank=True)
    imputation_visible = models.BooleanField(default=False)
    extra_position = models.PositiveSmallIntegerField(null=True, blank=True)
    extra_visible = models.BooleanField(default=False)
    scst_position = models.PositiveSmallIntegerField(null=True, blank=True)
    scst_visible = models.BooleanField(default=False)
    colt_id_position = models.PositiveSmallIntegerField(null=True, blank=True)
    colt_id_visible = models.BooleanField(default=False)

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.app)        


class Day(models.Model):

    date = models.DateField()
    has_content = models.BooleanField(default=False)

    app = models.ForeignKey('App', on_delete=models.CASCADE)
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

    def __str__(self):
        return '[#{0}] {1} ({2})'.format(
            self.id, self.date, self.app.team.name)


class Cell(models.Model):

    date = models.DateField()
    presence = models.CharField(max_length=20, blank=True, null=True)
    absence = models.CharField(max_length=20, blank=True, null=True)
    short = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
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

    def __str__(self):
        return '[#{0}] {1} ({2})'.format(
            self.id, self.date, self.profile.name)


class Work(models.Model):

    description = models.TextField(null=True, blank=True)
    description_bg_color = models.CharField(max_length=20, blank=True, null=True)
    description_text_color = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(null=True, blank=True)
    note_bg_color = models.CharField(max_length=20, blank=True, null=True)
    note_text_color = models.CharField(max_length=20, blank=True, null=True)
    ilt = models.TextField(null=True, blank=True)
    ilt_bg_color = models.CharField(max_length=20, blank=True, null=True)
    ilt_text_color = models.CharField(max_length=20, blank=True, null=True)
    upm = models.TextField(null=True, blank=True)
    upm_bg_color = models.CharField(max_length=20, blank=True, null=True)
    upm_text_color = models.CharField(max_length=20, blank=True, null=True)
    status = models.TextField(null=True, blank=True)
    status_bg_color = models.CharField(max_length=20, blank=True, null=True)
    status_text_color = models.CharField(max_length=20, blank=True, null=True)
    zkl = models.TextField(null=True, blank=True)
    zkl_bg_color = models.CharField(max_length=20, blank=True, null=True)
    zkl_text_color = models.CharField(max_length=20, blank=True, null=True)
    cascat = models.TextField(null=True, blank=True)
    cascat_bg_color = models.CharField(max_length=20, blank=True, null=True)
    cascat_text_color = models.CharField(max_length=20, blank=True, null=True)
    grue = models.TextField(null=True, blank=True)
    grue_bg_color = models.CharField(max_length=20, blank=True, null=True)
    grue_text_color = models.CharField(max_length=20, blank=True, null=True)
    osv = models.TextField(null=True, blank=True)
    osv_bg_color = models.CharField(max_length=20, blank=True, null=True)
    osv_text_color = models.CharField(max_length=20, blank=True, null=True)
    loco = models.TextField(null=True, blank=True)
    loco_bg_color = models.CharField(max_length=20, blank=True, null=True)
    loco_text_color = models.CharField(max_length=20, blank=True, null=True)
    hgs = models.TextField(null=True, blank=True)
    hgs_bg_color = models.CharField(max_length=20, blank=True, null=True)
    hgs_text_color = models.CharField(max_length=20, blank=True, null=True)
    soudure = models.TextField(null=True, blank=True)
    soudure_bg_color = models.CharField(max_length=20, blank=True, null=True)
    soudure_text_color = models.CharField(max_length=20, blank=True, null=True)
    pn = models.TextField(null=True, blank=True)
    pn_bg_color = models.CharField(max_length=20, blank=True, null=True)
    pn_text_color = models.CharField(max_length=20, blank=True, null=True)
    art = models.TextField(null=True, blank=True)
    art_bg_color = models.CharField(max_length=20, blank=True, null=True)
    art_text_color = models.CharField(max_length=20, blank=True, null=True)
    s428 = models.TextField(null=True, blank=True)
    s428_bg_color = models.CharField(max_length=20, blank=True, null=True)
    s428_text_color = models.CharField(max_length=20, blank=True, null=True)
    s461 = models.TextField(null=True, blank=True)
    s461_bg_color = models.CharField(max_length=20, blank=True, null=True)
    s461_text_color = models.CharField(max_length=20, blank=True, null=True)
    atwtx = models.TextField(null=True, blank=True)
    atwtx_bg_color = models.CharField(max_length=20, blank=True, null=True)
    atwtx_text_color = models.CharField(max_length=20, blank=True, null=True)
    imputation = models.TextField(null=True, blank=True)
    imputation_bg_color = models.CharField(max_length=20, blank=True, null=True)
    imputation_text_color = models.CharField(max_length=20, blank=True, null=True)
    extra = models.TextField(null=True, blank=True)
    extra_bg_color = models.CharField(max_length=20, blank=True, null=True)
    extra_text_color = models.CharField(max_length=20, blank=True, null=True)
    scst = models.TextField(null=True, blank=True)
    scst_bg_color = models.CharField(max_length=20, blank=True, null=True)
    scst_text_color = models.CharField(max_length=20, blank=True, null=True)
    colt_id = models.PositiveIntegerField(null=True, blank=True)
    colt_id_bg_color = models.CharField(max_length=20, blank=True, null=True)
    colt_id_text_color = models.CharField(max_length=20, blank=True, null=True)
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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.description[:10])


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

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}]'.format(self.id)


class S460(models.Model):

    lane = models.CharField(max_length=100, blank=True, null=True)
    start = models.CharField(max_length=100, blank=True, null=True)
    end = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}]'.format(self.id)


class Shift(models.Model):

    date = models.DateField()
    shift = models.CharField(max_length=100, blank=True, null=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1} | {2}'.format(self.id, self.date, self.shift)


class Part(models.Model):

    date = models.DateField()

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', null=True, on_delete=models.SET_NULL)

    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        through='PartProfileLink',
    )

    def __str__(self):
        return '[#{0}] {1} [{2}] [{3}]'.format(
            self.id, self.date, self.team.name, self.work.description)


class Project(models.Model):

    name = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    date = models.DateField()

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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Template(models.Model):

    name = models.TextField(null=True, blank=True)

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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Subtask(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Note(models.Model):

    value = models.TextField(null=True, blank=True)
    date = models.DateField()

    profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.value)


class File(models.Model):

    type = models.CharField(max_length=100, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    extension = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '[#{0}] {1}.{2}'.format(self.id, self.name, self.extension)


class Input(models.Model):

    type = models.CharField(max_length=100, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    heading = models.BooleanField(default=False)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.name, self.value)


class Link(models.Model):

    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.name, self.url)


class Call(models.Model):

    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    start = models.TextField(null=True, blank=True)
    end = models.TextField(null=True, blank=True)

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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Leave(models.Model):

    year = models.PositiveSmallIntegerField()
    cn = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    jc = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    cv = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    ch = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    rh = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    rr = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    hs = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    def __str__(self):
        return '{0} - {1}'.format(self.profile, self.year)


class RR(models.Model):

    date = models.DateField()

    def __str__(self):
        return '{0}'.format(self.date)


#######################################################
######################## Links ########################
#######################################################


class TeamProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    watcher_is_manager = models.BooleanField(default=False)
    watcher_is_editor = models.BooleanField(default=False)
    watcher_is_visible = models.BooleanField(default=False)
    watcher_is_printable = models.BooleanField(default=False)
    watcher_can_see_cells = models.BooleanField(default=False)
    watcher_can_see_quotas = models.BooleanField(default=False)

    draft_is_manager = models.BooleanField(default=False)
    draft_is_editor = models.BooleanField(default=False)
    draft_is_user = models.BooleanField(default=False)
    draft_can_see_private = models.BooleanField(default=False)

    radium_is_manager = models.BooleanField(default=False)
    radium_is_editor = models.BooleanField(default=False)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.team.name)


class AppWorkLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.work)


class AppProjectLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.project)


class AppTaskLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.task)


class DayTaskLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.task)


class DayNoteLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.note)


class DayFileLink(models.Model):

    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.file)


class CellTaskLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.task)


class CellNoteLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.note)


class CellFileLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.file)


class CellCallLink(models.Model):

    cell = models.ForeignKey('Cell', on_delete=models.CASCADE)
    call = models.ForeignKey('Call', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.call)


class CallFileLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.call, self.file)


class CallLinkLink(models.Model):

    call = models.ForeignKey('Call', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.call, self.link)


class WorkFileLink(models.Model):

    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.work, self.file)


class PartProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    part = models.ForeignKey('Part', on_delete=models.CASCADE)

    is_participant = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return '{0} : {1}'.format(self.profile.name, self.part)


class ProjectTaskLink(models.Model):

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.task)


class AppTemplateLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    template = models.ForeignKey('Template', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.template)


class TemplateInputLink(models.Model):

    template = models.ForeignKey('Template', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.template, self.input)


class TaskSubtaskLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    subtask = models.ForeignKey('Subtask', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.subtask)


class TaskNoteLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.note)


class TaskFileLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.file)


class TaskInputLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    input = models.ForeignKey('Input', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.input)


class TaskLinkLink(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    link = models.ForeignKey('Link', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.link)