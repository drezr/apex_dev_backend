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
        related_name='%(app_label)s_%(class)s_profile',
    )

    def __str__(self):
        return self.name


class Circle(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Team(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)

    circle = models.ForeignKey('Circle', on_delete=models.CASCADE)
    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        related_name='%(app_label)s_%(class)s_circles',
        through='TeamProfileLink',
    )

    def __str__(self):
        return '[{0}] {1} ({2})'.format(
            self.id, self.name, self.app
        )


class App(models.Model):

    app = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    def __str__(self):
        return '[{0}] {1} ({2})'.format(self.id, self.app, self.name)


class Day(models.Model):

    date = models.DateField()
    has_content = models.BooleanField(default=False)

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        related_name='%(app_label)s_%(class)s_days',
        through='DayTaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        related_name='%(app_label)s_%(class)s_days',
        through='DayNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        related_name='%(app_label)s_%(class)s_days',
        through='DayFileLink',
    )

    def __str__(self):
        return '[{0}] {1} ({2})'.format(
            self.id, self.date, self.circle.name)


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
        related_name='%(app_label)s_%(class)s_cells',
        through='CellTaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        related_name='%(app_label)s_%(class)s_cells',
        through='CellNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        related_name='%(app_label)s_%(class)s_cells',
        through='CellFileLink',
    )
    calls = models.ManyToManyField(
        'Call',
        blank=True,
        related_name='%(app_label)s_%(class)s_cells',
        through='CellCallLink',
    )

    def __str__(self):
        return '[{0}] {1} ({2})'.format(
            self.id, self.date, self.profile.name)


class Work(models.Model):

    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    ilt = models.TextField(null=True, blank=True)
    upm = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    zkl = models.TextField(null=True, blank=True)
    cascat = models.TextField(null=True, blank=True)
    grue = models.TextField(null=True, blank=True)
    osv = models.TextField(null=True, blank=True)
    loco = models.TextField(null=True, blank=True)
    hgs = models.TextField(null=True, blank=True)
    soudure = models.TextField(null=True, blank=True)
    pn = models.TextField(null=True, blank=True)
    art = models.TextField(null=True, blank=True)
    s428 = models.TextField(null=True, blank=True)
    s461 = models.TextField(null=True, blank=True)
    atwtx = models.TextField(null=True, blank=True)
    imputation = models.TextField(null=True, blank=True)
    extra = models.TextField(null=True, blank=True)
    scst = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    apps = models.ManyToManyField(
        'App',
        blank=True,
        related_name='%(app_label)s_%(class)s_works',
        through='AppWorkLink',
    )

    files = models.ManyToManyField(
        'File',
        blank=True,
        related_name='%(app_label)s_%(class)s_works',
        through='WorkFileLink',
    )

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.description[:10])


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
        return '[{0}]'.format(self.id)


class S460(models.Model):

    lane = models.CharField(max_length=100, blank=True, null=True)
    start = models.CharField(max_length=100, blank=True, null=True)
    end = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[{0}]'.format(self.id)


class Shift(models.Model):

    date = models.DateField()
    shift = models.CharField(max_length=100, blank=True, null=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[{0}] {1} | {2}'.format(self.id, self.date, self.shift)


class Part(models.Model):

    date = models.DateField()

    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', null=True, on_delete=models.SET_NULL)

    profiles = models.ManyToManyField(
        'Profile',
        blank=True,
        related_name='%(app_label)s_%(class)s_parts',
        through='PartProfileLink',
    )

    def __str__(self):
        return '[{0}] {1} [{2}] [{3}]'.format(
            self.id, self.date, self.name, self.work.name)


class Project(models.Model):

    name = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    date = models.DateField()

    app = models.ForeignKey('app', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(
        'Task',
        blank=True,
        related_name='%(app_label)s_%(class)s_projects',
        through='ProjectTaskLink',
    )

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Model(models.Model):

    name = models.TextField(null=True, blank=True)

    app = models.ForeignKey('app', on_delete=models.CASCADE)
    fields = models.ManyToManyField(
        'Field',
        blank=True,
        related_name='%(app_label)s_%(class)s_models',
        through='ModelFieldLink',
    )

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Task(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    subtasks = models.ManyToManyField(
        'Subtask',
        blank=True,
        related_name='%(app_label)s_%(class)s_tasks',
        through='TaskSubtaskLink',
    )
    notes = models.ManyToManyField(
        'Note',
        blank=True,
        related_name='%(app_label)s_%(class)s_tasks',
        through='TaskNoteLink',
    )
    files = models.ManyToManyField(
        'File',
        blank=True,
        related_name='%(app_label)s_%(class)s_tasks',
        through='TaskFileLink',
    )
    fields = models.ManyToManyField(
        'Field',
        blank=True,
        related_name='%(app_label)s_%(class)s_tasks',
        through='TaskFieldLink',
    )

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Subtask(models.Model):

    name = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Note(models.Model):

    value = models.TextField(null=True, blank=True)
    date = models.DateField()

    profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.value)


class File(models.Model):

    name = models.TextField(null=True, blank=True)
    extension = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '[{0}] {1}.{2}'.format(self.id, self.name, self.extension)


class Field(models.Model):

    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    heading = models.BooleanField(default=False)

    def __str__(self):
        return '[{0}] {1} : {2}'.format(self.id, self.name, self.value)


class Call(models.Model):

    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    start = models.TextField(null=True, blank=True)
    end = models.TextField(null=True, blank=True)

    def __str__(self):
        return '[{0}] {1}'.format(self.id, self.name)


class Leave(models.Model):

    year = models.SmallIntegerField()
    cn = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    jc = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    cv = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    ch = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    rh = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    rr = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    hs = models.DecimalField(default=0, max_digits=6, decimal_places=2)

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

    profile = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_profiles'
    )
    team = models.ForeignKey(
        'Team', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_teams'
    )

    is_manager = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_printable = models.BooleanField(default=True)
    can_see_private = models.BooleanField(default=False)
    can_see_cells = models.BooleanField(default=False)
    can_see_quotas = models.BooleanField(default=False)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return '{0} : {1}'.format(
            self.profile.name, self.circle
        )


class AppWorkLink(models.Model):

    app = models.ForeignKey(
        'App', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_apps'
    )
    work = models.ForeignKey(
        'Work', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_works'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.circle, self.work)


class DayTaskLink(models.Model):

    day = models.ForeignKey(
        'Day', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_days'
    )
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.task)


class DayNoteLink(models.Model):

    day = models.ForeignKey(
        'Day', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_days'
    )
    note = models.ForeignKey(
        'Note', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_notes'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.note)


class DayFileLink(models.Model):

    day = models.ForeignKey(
        'Day', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_days'
    )
    file = models.ForeignKey(
        'File', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_files'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.day, self.file)


class CellTaskLink(models.Model):

    cell = models.ForeignKey(
        'Cell', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_cells'
    )
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.task)


class CellNoteLink(models.Model):

    cell = models.ForeignKey(
        'Cell', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_cells'
    )
    note = models.ForeignKey(
        'Note', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_notes'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.note)


class CellFileLink(models.Model):

    cell = models.ForeignKey(
        'Cell', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_cells'
    )
    file = models.ForeignKey(
        'File', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_files'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.file)


class CellCallLink(models.Model):

    cell = models.ForeignKey(
        'Cell', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_cells'
    )
    call = models.ForeignKey(
        'Call', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_calls'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.cell, self.call)


class WorkFileLink(models.Model):

    work = models.ForeignKey(
        'Work', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_works'
    )
    file = models.ForeignKey(
        'File', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_files'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.work, self.file)


class PartProfileLink(models.Model):

    profile = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_profiles'
    )
    part = models.ForeignKey(
        'Part', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_parts'
    )

    is_participant = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return '{0} : {1}'.format(
            self.profile.name, self.part
        )


class ProjectTaskLink(models.Model):

    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_projects'
    )
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.task)


class ModelFieldLink(models.Model):

    model = models.ForeignKey(
        'Model', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_models'
    )
    field = models.ForeignKey(
        'Field', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_fields'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.model, self.field)


class TaskSubtaskLink(models.Model):

    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )
    subtask = models.ForeignKey(
        'Subtask', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_subtasks'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.subtask)


class TaskNoteLink(models.Model):

    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )
    note = models.ForeignKey(
        'Note', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_notes'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.note)


class TaskFileLink(models.Model):

    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )
    file = models.ForeignKey(
        'File', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_files'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.file)


class TaskFieldLink(models.Model):

    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_tasks'
    )
    field = models.ForeignKey(
        'Field', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_fields'
    )

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.field)