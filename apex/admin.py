from django.contrib import admin

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )


class TeamAdmin(admin.ModelAdmin):
    raw_id_fields = ('circle', )


class AppAdmin(admin.ModelAdmin):
    raw_id_fields = ('team', )


class DayAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class CellAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class LimitAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class S460Admin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class ShiftAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class PartAdmin(admin.ModelAdmin):
    raw_id_fields = ('shift', 'project', 'team', 'work', )


class ProjectAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class ModelAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class NoteAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Circle)
admin.site.register(Team, TeamAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Cell, CellAdmin)
admin.site.register(Work)
admin.site.register(Limit, LimitAdmin)
admin.site.register(S460, S460Admin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(Note, NoteAdmin)
admin.site.register(File)
admin.site.register(Call)
admin.site.register(Leave)
admin.site.register(RR)


class TeamProfileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'team', )


class AppWorkLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'work', )


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


class PartProfileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('part', 'profile', )


class ProjectTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('project', 'task', )


class ModelFieldLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('model', 'field', )


class TaskSubtaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'subtask', )


class TaskNoteLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'note', )


class TaskFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'file', )


class TaskFieldLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('task', 'field', )


admin.site.register(TeamProfileLink, TeamProfileLinkAdmin)
admin.site.register(AppWorkLink, AppWorkLinkAdmin)
admin.site.register(DayTaskLink, DayTaskLinkAdmin)
admin.site.register(DayNoteLink, DayNoteLinkAdmin)
admin.site.register(DayFileLink, DayFileLinkAdmin)
admin.site.register(CellTaskLink, CellTaskLinkAdmin)
admin.site.register(CellNoteLink, CellNoteLinkAdmin)
admin.site.register(CellFileLink, CellFileLinkAdmin)
admin.site.register(CellCallLink, CellCallLinkAdmin)
admin.site.register(WorkFileLink, WorkFileLinkAdmin)
admin.site.register(PartProfileLink, PartProfileLinkAdmin)
admin.site.register(ProjectTaskLink, ProjectTaskLinkAdmin)
admin.site.register(ModelFieldLink, ModelFieldLinkAdmin)
admin.site.register(TaskSubtaskLink, TaskSubtaskLinkAdmin)
admin.site.register(TaskNoteLink, TaskNoteLinkAdmin)
admin.site.register(TaskFileLink, TaskFileLinkAdmin)
admin.site.register(TaskFieldLink, TaskFieldLinkAdmin)