from django.contrib import admin

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )
    readonly_fields = ('created_date', 'updated_date', )


class TeamAdmin(admin.ModelAdmin):
    raw_id_fields = ('circle', )


class AppAdmin(admin.ModelAdmin):
    raw_id_fields = ('team', 'profile', 'template', )


class RadiumConfigAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class RadiumConfigColumnAdmin(admin.ModelAdmin):
    raw_id_fields = ('config', )


class WorkFieldAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class WorkFieldExtendAdmin(admin.ModelAdmin):
    raw_id_fields = ('work_field', )


class DayAdmin(admin.ModelAdmin):
    raw_id_fields = ('team', )


class CellAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class ShiftAdmin(admin.ModelAdmin):
    raw_id_fields = ('work', )


class PartAdmin(admin.ModelAdmin):
    raw_id_fields = ('shift', 'project', 'team', )


class NoteAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class QuotaAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', )


class LeaveConfigAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', )


class LeaveTypeAdmin(admin.ModelAdmin):
    raw_id_fields = ('config', )


class LogAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'work', 'cell', )


class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('profile', 'app', )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Circle)
admin.site.register(Team, TeamAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(RadiumConfig, RadiumConfigAdmin)
admin.site.register(RadiumConfigColumn, RadiumConfigColumnAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Cell, CellAdmin)
admin.site.register(Work)
admin.site.register(WorkField, WorkFieldAdmin)
admin.site.register(WorkFieldExtend, WorkFieldExtendAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Project)
admin.site.register(Folder)
admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(Note, NoteAdmin)
admin.site.register(File)
admin.site.register(Input)
admin.site.register(Link)
admin.site.register(Call)
admin.site.register(Quota, QuotaAdmin)
admin.site.register(LeaveConfig, LeaveConfigAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(Holiday)
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


class AppContactLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'contact', )


class AppFolderLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'folder', )


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


class FolderTaskLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('folder', 'task', )


class FolderNoteLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('folder', 'note', )


class FolderFileLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('folder', 'file', )


class FolderLinkLinkAdmin(admin.ModelAdmin):
    raw_id_fields = ('folder', 'link', )


admin.site.register(TeamProfileLink, TeamProfileLinkAdmin)
admin.site.register(AppWorkLink, AppWorkLinkAdmin)
admin.site.register(AppProjectLink, AppProjectLinkAdmin)
admin.site.register(AppTaskLink, AppTaskLinkAdmin)
admin.site.register(AppContactLink, AppContactLinkAdmin)
admin.site.register(AppFolderLink, AppFolderLinkAdmin)
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
admin.site.register(TaskSubtaskLink, TaskSubtaskLinkAdmin)
admin.site.register(TaskNoteLink, TaskNoteLinkAdmin)
admin.site.register(TaskFileLink, TaskFileLinkAdmin)
admin.site.register(TaskInputLink, TaskInputLinkAdmin)
admin.site.register(TaskLinkLink, TaskLinkLinkAdmin)
admin.site.register(FolderTaskLink, FolderTaskLinkAdmin)
admin.site.register(FolderNoteLink, FolderNoteLinkAdmin)
admin.site.register(FolderFileLink, FolderFileLinkAdmin)
admin.site.register(FolderLinkLink, FolderLinkLinkAdmin)