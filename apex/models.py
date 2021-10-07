from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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

    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
    
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

    def __str__(self):
        name = None

        if self.team:
            name = 'Team : ' + self.team.name

        elif self.profile:
            name = 'Profile : ' + self.profile.name

        return '[#{0}] {1} ({2})'.format(self.id, self.app, name)


class RadiumConfig(models.Model):

    shifts_position = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
    shifts_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    shifts_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    shifts_visible = models.BooleanField(default=True)
    description_position = models.PositiveSmallIntegerField(null=True, blank=True, default=1)
    description_width = models.PositiveSmallIntegerField(null=True, blank=True, default=400)
    description_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    description_visible = models.BooleanField(default=True)
    note_position = models.PositiveSmallIntegerField(null=True, blank=True, default=2)
    note_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    note_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    note_visible = models.BooleanField(default=True)
    ilt_position = models.PositiveSmallIntegerField(null=True, blank=True, default=3)
    ilt_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    ilt_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    ilt_visible = models.BooleanField(default=True)
    files_position = models.PositiveSmallIntegerField(null=True, blank=True, default=4)
    files_width = models.PositiveSmallIntegerField(null=True, blank=True, default=300)
    files_visible = models.BooleanField(default=True)
    upm_position = models.PositiveSmallIntegerField(null=True, blank=True, default=5)
    upm_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    upm_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    upm_visible = models.BooleanField(default=True)
    colt_position = models.PositiveSmallIntegerField(null=True, blank=True, default=6)
    colt_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    colt_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    colt_visible = models.BooleanField(default=True)
    status_position = models.PositiveSmallIntegerField(null=True, blank=True, default=7)
    status_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    status_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    status_visible = models.BooleanField(default=True)
    limits_position = models.PositiveSmallIntegerField(null=True, blank=True, default=8)
    limits_width = models.PositiveSmallIntegerField(null=True, blank=True, default=600)
    limits_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    limits_visible = models.BooleanField(default=True)
    s460s_position = models.PositiveSmallIntegerField(null=True, blank=True, default=9)
    s460s_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    s460s_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    s460s_visible = models.BooleanField(default=True)
    zkl_position = models.PositiveSmallIntegerField(null=True, blank=True, default=10)
    zkl_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    zkl_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    zkl_visible = models.BooleanField(default=True)
    cascat_position = models.PositiveSmallIntegerField(null=True, blank=True, default=11)
    cascat_width = models.PositiveSmallIntegerField(null=True, blank=True, default=150)
    cascat_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    cascat_visible = models.BooleanField(default=True)
    grue_position = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    grue_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    grue_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    grue_visible = models.BooleanField(default=True)
    osv_position = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    osv_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    osv_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    osv_visible = models.BooleanField(default=True)
    loco_position = models.PositiveSmallIntegerField(null=True, blank=True, default=14)
    loco_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    loco_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    loco_visible = models.BooleanField(default=True)
    hgs_position = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    hgs_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    hgs_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    hgs_visible = models.BooleanField(default=True)
    soudure_position = models.PositiveSmallIntegerField(null=True, blank=True, default=16)
    soudure_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    soudure_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    soudure_visible = models.BooleanField(default=True)
    pn_position = models.PositiveSmallIntegerField(null=True, blank=True, default=17)
    pn_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    pn_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    pn_visible = models.BooleanField(default=True)
    art_position = models.PositiveSmallIntegerField(null=True, blank=True, default=18)
    art_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    art_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    art_visible = models.BooleanField(default=True)
    s428_position = models.PositiveSmallIntegerField(null=True, blank=True, default=19)
    s428_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    s428_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    s428_visible = models.BooleanField(default=True)
    s461_position = models.PositiveSmallIntegerField(null=True, blank=True, default=20)
    s461_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    s461_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    s461_visible = models.BooleanField(default=True)
    atwtx_position = models.PositiveSmallIntegerField(null=True, blank=True, default=21)
    atwtx_width = models.PositiveSmallIntegerField(null=True, blank=True, default=150)
    atwtx_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    atwtx_visible = models.BooleanField(default=True)
    imputation_position = models.PositiveSmallIntegerField(null=True, blank=True, default=22)
    imputation_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    imputation_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    imputation_visible = models.BooleanField(default=True)
    extra_position = models.PositiveSmallIntegerField(null=True, blank=True, default=23)
    extra_width = models.PositiveSmallIntegerField(null=True, blank=True, default=100)
    extra_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    extra_visible = models.BooleanField(default=True)
    line_position = models.PositiveSmallIntegerField(null=True, blank=True, default=24)
    line_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    line_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    line_visible = models.BooleanField(default=True)
    supervisor_position = models.PositiveSmallIntegerField(null=True, blank=True, default=25)
    supervisor_width = models.PositiveSmallIntegerField(null=True, blank=True, default=150)
    supervisor_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    supervisor_visible = models.BooleanField(default=True)

    printable_shifts_position = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
    printable_shifts_width = models.PositiveSmallIntegerField(null=True, blank=True, default=160)
    printable_shifts_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_shifts_visible = models.BooleanField(default=True)
    printable_description_position = models.PositiveSmallIntegerField(null=True, blank=True, default=1)
    printable_description_width = models.PositiveSmallIntegerField(null=True, blank=True, default=300)
    printable_description_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_description_visible = models.BooleanField(default=True)
    printable_note_position = models.PositiveSmallIntegerField(null=True, blank=True, default=2)
    printable_note_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    printable_note_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_note_visible = models.BooleanField(default=True)
    printable_ilt_position = models.PositiveSmallIntegerField(null=True, blank=True, default=3)
    printable_ilt_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_ilt_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_ilt_visible = models.BooleanField(default=True)
    printable_upm_position = models.PositiveSmallIntegerField(null=True, blank=True, default=5)
    printable_upm_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_upm_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_upm_visible = models.BooleanField(default=True)
    printable_colt_position = models.PositiveSmallIntegerField(null=True, blank=True, default=6)
    printable_colt_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_colt_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_colt_visible = models.BooleanField(default=True)
    printable_status_position = models.PositiveSmallIntegerField(null=True, blank=True, default=7)
    printable_status_width = models.PositiveSmallIntegerField(null=True, blank=True, default=200)
    printable_status_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_status_visible = models.BooleanField(default=True)
    printable_limits_position = models.PositiveSmallIntegerField(null=True, blank=True, default=8)
    printable_limits_width = models.PositiveSmallIntegerField(null=True, blank=True, default=500)
    printable_limits_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    printable_limits_visible = models.BooleanField(default=True)
    printable_s460s_position = models.PositiveSmallIntegerField(null=True, blank=True, default=9)
    printable_s460s_width = models.PositiveSmallIntegerField(null=True, blank=True, default=160)
    printable_s460s_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    printable_s460s_visible = models.BooleanField(default=True)
    printable_zkl_position = models.PositiveSmallIntegerField(null=True, blank=True, default=10)
    printable_zkl_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_zkl_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_zkl_visible = models.BooleanField(default=True)
    printable_cascat_position = models.PositiveSmallIntegerField(null=True, blank=True, default=11)
    printable_cascat_width = models.PositiveSmallIntegerField(null=True, blank=True, default=125)
    printable_cascat_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_cascat_visible = models.BooleanField(default=True)
    printable_grue_position = models.PositiveSmallIntegerField(null=True, blank=True, default=12)
    printable_grue_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_grue_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_grue_visible = models.BooleanField(default=True)
    printable_osv_position = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_osv_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_osv_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_osv_visible = models.BooleanField(default=True)
    printable_loco_position = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_loco_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_loco_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_loco_visible = models.BooleanField(default=True)
    printable_hgs_position = models.PositiveSmallIntegerField(null=True, blank=True, default=15)
    printable_hgs_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_hgs_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_hgs_visible = models.BooleanField(default=True)
    printable_soudure_position = models.PositiveSmallIntegerField(null=True, blank=True, default=16)
    printable_soudure_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_soudure_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_soudure_visible = models.BooleanField(default=True)
    printable_pn_position = models.PositiveSmallIntegerField(null=True, blank=True, default=17)
    printable_pn_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_pn_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_pn_visible = models.BooleanField(default=True)
    printable_art_position = models.PositiveSmallIntegerField(null=True, blank=True, default=18)
    printable_art_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_art_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_art_visible = models.BooleanField(default=True)
    printable_s428_position = models.PositiveSmallIntegerField(null=True, blank=True, default=19)
    printable_s428_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_s428_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_s428_visible = models.BooleanField(default=True)
    printable_s461_position = models.PositiveSmallIntegerField(null=True, blank=True, default=20)
    printable_s461_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_s461_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_s461_visible = models.BooleanField(default=True)
    printable_atwtx_position = models.PositiveSmallIntegerField(null=True, blank=True, default=21)
    printable_atwtx_width = models.PositiveSmallIntegerField(null=True, blank=True, default=125)
    printable_atwtx_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_atwtx_visible = models.BooleanField(default=True)
    printable_imputation_position = models.PositiveSmallIntegerField(null=True, blank=True, default=22)
    printable_imputation_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_imputation_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_imputation_visible = models.BooleanField(default=True)
    printable_extra_position = models.PositiveSmallIntegerField(null=True, blank=True, default=23)
    printable_extra_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_extra_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_extra_visible = models.BooleanField(default=True)
    printable_line_position = models.PositiveSmallIntegerField(null=True, blank=True, default=24)
    printable_line_width = models.PositiveSmallIntegerField(null=True, blank=True, default=75)
    printable_line_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_line_visible = models.BooleanField(default=True)
    printable_supervisor_position = models.PositiveSmallIntegerField(null=True, blank=True, default=25)
    printable_supervisor_width = models.PositiveSmallIntegerField(null=True, blank=True, default=120)
    printable_supervisor_textsize = models.PositiveSmallIntegerField(null=True, blank=True, default=13)
    printable_supervisor_visible = models.BooleanField(default=True)

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
        return '[#{0}] {1}'.format(self.id, self.work.description)


class S460(models.Model):

    line = models.CharField(max_length=100, blank=True, null=True)
    lane = models.CharField(max_length=100, blank=True, null=True)
    start = models.CharField(max_length=100, blank=True, null=True)
    end = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.work.description)


class Shift(models.Model):

    date = models.DateField()
    shift = models.CharField(max_length=100, blank=True, null=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1} | {2}'.format(self.id, self.date, self.shift)


class Part(models.Model):

    date = models.DateField()
    needs = models.CharField(max_length=255, blank=True, null=True)
    locked = models.BooleanField(default=False)

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

    def __str__(self):
        return '[#{0}] {1} [{2}] [{3}]'.format(
            self.id, self.team.name, self.date, self.work.description)


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

    kind = models.CharField(max_length=100, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    extension = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return '[#{0}] {1}.{2}'.format(self.id, self.name, self.extension)


class Input(models.Model):

    kind = models.CharField(max_length=100, blank=True, null=True)
    key = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    heading = models.BooleanField(default=False)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.key, self.value)


class Link(models.Model):

    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.name, self.url)


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

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.name)


class Leave(models.Model):

    year = models.PositiveSmallIntegerField()
    type_0 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_1 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_2 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_3 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_4 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_5 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_6 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_7 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_8 = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type_9 = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1}'.format(self.profile, self.year)


class LeaveConfig(models.Model):

    leave_count = models.PositiveSmallIntegerField(default=0)
    leave_0_name = models.CharField(max_length=10, blank=True, null=True)
    leave_0_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_0_type = models.CharField(max_length=20, default='day')
    leave_0_color = models.CharField(max_length=20, default='red')
    leave_1_name = models.CharField(max_length=10, blank=True, null=True)
    leave_1_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_1_type = models.CharField(max_length=20, default='day')
    leave_1_color = models.CharField(max_length=20, default='red')
    leave_2_name = models.CharField(max_length=10, blank=True, null=True)
    leave_2_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_2_type = models.CharField(max_length=20, default='day')
    leave_2_color = models.CharField(max_length=20, default='red')
    leave_3_name = models.CharField(max_length=10, blank=True, null=True)
    leave_3_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_3_type = models.CharField(max_length=20, default='day')
    leave_3_color = models.CharField(max_length=20, default='red')
    leave_4_name = models.CharField(max_length=10, blank=True, null=True)
    leave_4_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_4_type = models.CharField(max_length=20, default='day')
    leave_4_color = models.CharField(max_length=20, default='red')
    leave_5_name = models.CharField(max_length=10, blank=True, null=True)
    leave_5_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_5_type = models.CharField(max_length=20, default='day')
    leave_5_color = models.CharField(max_length=20, default='red')
    leave_6_name = models.CharField(max_length=10, blank=True, null=True)
    leave_6_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_6_type = models.CharField(max_length=20, default='day')
    leave_6_color = models.CharField(max_length=20, default='red')
    leave_7_name = models.CharField(max_length=10, blank=True, null=True)
    leave_7_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_7_type = models.CharField(max_length=20, default='day')
    leave_7_color = models.CharField(max_length=20, default='red')
    leave_8_name = models.CharField(max_length=10, blank=True, null=True)
    leave_8_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_8_type = models.CharField(max_length=20, default='day')
    leave_8_color = models.CharField(max_length=20, default='red')
    leave_9_name = models.CharField(max_length=10, blank=True, null=True)
    leave_9_desc = models.CharField(max_length=50, blank=True, null=True)
    leave_9_type = models.CharField(max_length=20, default='day')
    leave_9_color = models.CharField(max_length=20, default='red')

    app = models.ForeignKey('App', on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.app)


class RR(models.Model):

    date = models.DateField()

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.date)


class Log(models.Model):

    field = models.CharField(max_length=255, blank=True, null=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    profile = models.ForeignKey('Profile', null=True, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)
    cell = models.ForeignKey('Cell', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1} : {2}'.format(self.id, self.field, self.profile.name)


class Message(models.Model):

    priority = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    author = models.ForeignKey('Profile', null=True, on_delete=models.CASCADE, related_name='author')
    profile = models.ForeignKey('Profile', null=True, blank=True, on_delete=models.CASCADE)
    app = models.ForeignKey('App', null=True, blank=True, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return '[#{0}] {1}'.format(self.id, self.message)


#######################################################
######################## Links ########################
#######################################################


class TeamProfileLink(models.Model):

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    is_manager = models.BooleanField(default=False)

    draft_is_editor = models.BooleanField(default=False)
    draft_is_user = models.BooleanField(default=False)
    draft_can_see_private = models.BooleanField(default=False)

    radium_is_editor = models.BooleanField(default=False)

    watcher_is_editor = models.BooleanField(default=False)
    watcher_is_visible = models.BooleanField(default=False)
    watcher_is_printable = models.BooleanField(default=False)
    watcher_can_see_cells = models.BooleanField(default=False)
    watcher_can_see_quotas = models.BooleanField(default=False)
    watcher_color = models.CharField(max_length=20, blank=True, null=True)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

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


class AppFileLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    file = models.ForeignKey('File', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.file)


class AppNoteLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.note)


class AppContactLink(models.Model):

    app = models.ForeignKey('App', on_delete=models.CASCADE)
    contact = models.ForeignKey('Profile', on_delete=models.CASCADE)

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return '{0} : {1}'.format(self.app, self.contact)


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