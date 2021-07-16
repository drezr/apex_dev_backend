from django.contrib import admin

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )


class TeamAdmin(admin.ModelAdmin):
    raw_id_fields = ('circle', )


class AppAdmin(admin.ModelAdmin):
    raw_id_fields = ('team', )


class RadiumConfigAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class DayAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class CellAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class WorkAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'description_last_editor',
        'note_last_editor',
        'ilt_last_editor',
        'upm_last_editor',
        'status_last_editor',
        'zkl_last_editor',
        'cascat_last_editor',
        'grue_last_editor',
        'osv_last_editor',
        'loco_last_editor',
        'hgs_last_editor',
        'soudure_last_editor',
        'pn_last_editor',
        'art_last_editor',
        's428_last_editor',
        's461_last_editor',
        'atwtx_last_editor',
        'imputation_last_editor',
        'extra_last_editor',
        'scst_last_editor',
        'colt_id_last_editor',
    )


class LimitAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class S460Admin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class ShiftAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class PartAdmin(admin.ModelAdmin):
    raw_id_fields = ('shift', 'project', 'team', 'work', )


class NoteAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class LeaveAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class LogAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'work', 'cell', )


class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'app', )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Circle)
admin.site.register(Team, TeamAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(RadiumConfig, RadiumConfigAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Cell, CellAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(S460, S460Admin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Project)
admin.site.register(Template)
admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(Note, NoteAdmin)
admin.site.register(File)
admin.site.register(Input)
admin.site.register(Link)
admin.site.register(Call)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(RR)
admin.site.register(Log, LogAdmin)
admin.site.register(Message, MessageAdmin)


class TeamProfileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'team', )


class AppWorkLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'work', )


class AppProjectLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'project', )


class AppTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'task', )


class DayTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('day', 'task', )


class DayNoteLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('day', 'note', )


class DayFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('day', 'file', )


class CellTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('cell', 'task', )


class CellNoteLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('cell', 'note', )


class CellFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('cell', 'file', )


class CellCallLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('cell', 'call', )


class WorkFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', 'file', )


class CallFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('call', 'file', )


class CallLinkLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('call', 'link', )


class PartProfileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('part', 'profile', )


class ProjectTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('project', 'task', )


class AppTemplateLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'template', )


class TemplateInputLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('template', 'input', )


class TaskSubtaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'subtask', )


class TaskNoteLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'note', )


class TaskFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'file', )


class TaskInputLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'input', )


class TaskLinkLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'link', )


admin.site.register(TeamProfileLink, TeamProfileLinkAdmin)
admin.site.register(AppWorkLink, AppWorkLinkAdmin)
admin.site.register(AppProjectLink, AppProjectLinkAdmin)
admin.site.register(AppTaskLink, AppTaskLinkAdmin)
admin.site.register(DayTaskLink, DayTaskLinkAdmin)
admin.site.register(DayNoteLink, DayNoteLinkAdmin)
admin.site.register(DayFileLink, DayFileLinkAdmin)
admin.site.register(CellTaskLink, CellTaskLinkAdmin)
admin.site.register(CellNoteLink, CellNoteLinkAdmin)
admin.site.register(CellFileLink, CellFileLinkAdmin)
admin.site.register(CellCallLink, CellCallLinkAdmin)
admin.site.register(WorkFileLink, WorkFileLinkAdmin)
admin.site.register(CallFileLink, CallFileLinkAdmin)
admin.site.register(CallLinkLink, CallLinkLinkAdmin)
admin.site.register(PartProfileLink, PartProfileLinkAdmin)
admin.site.register(ProjectTaskLink, ProjectTaskLinkAdmin)
admin.site.register(AppTemplateLink, AppTemplateLinkAdmin)
admin.site.register(TemplateInputLink, TemplateInputLinkAdmin)
admin.site.register(TaskSubtaskLink, TaskSubtaskLinkAdmin)
admin.site.register(TaskNoteLink, TaskNoteLinkAdmin)
admin.site.register(TaskFileLink, TaskFileLinkAdmin)
admin.site.register(TaskInputLink, TaskInputLinkAdmin)
admin.site.register(TaskLinkLink, TaskLinkLinkAdmin)