from copy import deepcopy

from rest_framework import serializers

from .models import *


def context_check(context, arg, value):
    '''
    Generic way to check if a specific field is needed
    '''

    if context and arg in context and context[arg] == value:
        return True

    return False


def context_set_parent(context, new_parent_id, new_parent_type):
    '''
    Shortcut to pass the parent id and type to children's context
    '''

    context = deepcopy(context)
    context['parent_id'] = new_parent_id
    context['parent_type'] = new_parent_type

    return context


def get_link(parent, ctx, child_type):
    '''
    Generic way to retrieve the link beetween parents and children
    '''

    if context_check(ctx, 'link', 'detail'):
        if 'parent_id' in ctx:
            filters = dict()
            filters[ctx['parent_type']] = ctx['parent_id']
            filters[child_type] = parent.id

            link_model = globals()[
                ctx['parent_type'].capitalize() +
                child_type.capitalize() +
                'Link'
            ]

            serializer_model = globals()[
                ctx['parent_type'].capitalize() +
                child_type.capitalize() +
                'LinkSerializer'
            ]

            link = link_model.objects.get(**filters)

            return serializer_model(link).data


def get_children(parent, ctx, parent_type, child_type):
    '''
    Generic way to retrieve a parent's children
    '''

    def get_child_set(parent, child_type):
        '''
        Finds correct set name
        Sets name depends on link's type
        '''

        if hasattr(parent, child_type + '_set'):
            return getattr(parent, child_type + '_set')

        elif hasattr(parent, child_type + 's'):
            return getattr(parent, child_type + 's')

        else:
            raise Warning('Set not found')

    if context_check(ctx, child_type + 's', 'detail'):
        ctx = context_set_parent(ctx, parent.id, parent_type)
        child_set = get_child_set(parent, child_type)
        serializer = globals()[child_type.capitalize() + 'Serializer']

        return serializer(child_set.all(), many=True, context=ctx).data

    elif context_check(ctx, parent_type + 's', 'id'):
        child_set = get_child_set(parent, child_type)

        return [c.id for c in child_set.all()]


def get_child(parent, ctx, child_type):
    '''
    Generic way to retrieve a parent's child
    '''

    serializer = globals()[child_type.capitalize() + 'Serializer']
    child_set = getattr(parent, child_type)

    return serializer(child_set, context=ctx).data


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #
# @@@@@@@@@@@@@@@@ Models Serializers @@@@@@@@@@@@@@@ #
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #


class ProfileSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_staff = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'

    def get_link(self, profile):
        ctx = self.context
        
        if 'parent_type' in ctx and ctx['parent_type'] == 'app':
            return get_link(profile, ctx, 'contact')
        
        return get_link(profile, ctx, 'profile')

    def get_username(self, profile):
        return profile.user.username

    def get_is_staff(self, profile):
        return profile.user.is_staff

    def get_apps(self, team):
        return get_children(team, self.context, 'team', 'app')


class CircleSerializer(serializers.ModelSerializer):

    teams = serializers.SerializerMethodField()

    class Meta:
        model = Circle
        fields = '__all__'

    def get_teams(self, circle):
        return get_children(circle, self.context, 'circle', 'team')


class TeamSerializer(serializers.ModelSerializer):

    profiles = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'

    def get_profiles(self, team):
        return get_children(team, self.context, 'team', 'profile')

    def get_apps(self, team):
        return get_children(team, self.context, 'team', 'app')


class AppSerializer(serializers.ModelSerializer):

    projects = serializers.SerializerMethodField()
    #templates = serializers.SerializerMethodField()
    folders = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    #files = serializers.SerializerMethodField()
    #notes = serializers.SerializerMethodField()
    contacts = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = App
        fields = '__all__'

    def get_projects(self, app):
        return get_children(app, self.context, 'app', 'project')

    # def get_templates(self, app):
    #     return get_children(app, self.context, 'app', 'template')

    def get_folders(self, app):
        return get_children(app, self.context, 'app', 'folder')

    def get_tasks(self, app):
        return get_children(app, self.context, 'app', 'task')

    # def get_files(self, app):
    #     return get_children(app, self.context, 'app', 'file')

    # def get_notes(self, app):
    #     return get_children(app, self.context, 'app', 'note')

    def get_contacts(self, app):
        if 'contacts' in self.context:
            return ProfileSerializer(
                app.contacts.all(), many=True, context=self.context).data

    def get_message_count(self, app):
        if 'message_count' in self.context:
            return Message.objects.filter(app=app).count()

    def get_type(self, app):
        return 'app'


class RadiumConfigSerializer(serializers.ModelSerializer):

    columns = serializers.SerializerMethodField()

    class Meta:
        model = RadiumConfig
        fields = '__all__'

    def get_columns(self, config):
        return RadiumConfigColumnSerializer(
            config.column_set.all(), many=True).data


class RadiumConfigColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = RadiumConfigColumn
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_link(self, project):
        return get_link(project, self.context, 'project')

    def get_tasks(self, project):
        return get_children(project, self.context, 'project', 'task')

    def get_type(self, project):
        return 'project'


class FolderSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = '__all__'

    def get_tasks(self, folder):
        return get_children(folder, self.context, 'folder', 'task')

    def get_notes(self, folder):
        return get_children(folder, self.context, 'folder', 'note')

    def get_files(self, folder):
        return get_children(folder, self.context, 'folder', 'file')

    def get_link(self, folder):
        return get_link(folder, self.context, 'folder')

    def get_type(self, folder):
        return 'folder'


class TaskSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    subtasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    inputs = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    codes = serializers.SerializerMethodField()
    teammates = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_subtasks(self, task):
        return get_children(task, self.context, 'task', 'subtask')

    def get_notes(self, task):
        return get_children(task, self.context, 'task', 'note')

    def get_inputs(self, task):
        return get_children(task, self.context, 'task', 'input')

    def get_files(self, task):
        return get_children(task, self.context, 'task', 'file')

    def get_codes(self, task):
        return get_children(task, self.context, 'task', 'code')

    def get_link(self, task):
        return get_link(task, self.context, 'task')

    def get_type(self, task):
        return 'task'

    # -------- WIP --------
    def get_children(self, task):
        children = list()

        for _type in ['subtask', 'input', 'file', 'note']:
            elements = get_children(task, self.context, 'task', _type)
            [children.append(dict(c)) for c in elements]

        return children

    def get_teammates(self, task):
        if 'teammates' in self.context:
            cell_task_links = CellTaskLink.objects.filter(task=task)

            if self.context['teammates'] == 'detail':
                return [link.cell.profile.name for link in cell_task_links]

            elif self.context['teammates'] == 'id':
                return [link.cell.profile.id for link in cell_task_links]


class SubtaskSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Subtask
        fields = '__all__'

    def get_link(self, subtask):
        return get_link(subtask, self.context, 'subtask')

    def get_type(self, subtask):
        return 'subtask'


class NoteSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    teammates = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = '__all__'

    def get_link(self, note):
        return get_link(note, self.context, 'note')

    def get_author(self, note):
        return note.profile.name

    def get_teammates(self, note):
        if 'teammates' in self.context:
            cell_note_links = CellNoteLink.objects.filter(note=note)

            if self.context['teammates'] == 'detail':
                return [link.cell.profile.name for link in cell_note_links]

            elif self.context['teammates'] == 'id':
                return [link.cell.profile.id for link in cell_note_links]

    def get_type(self, note):
        return 'note'


class InputSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Input
        fields = '__all__'

    def get_link(self, input):
        return get_link(input, self.context, 'input')

    def get_type(self, input):
        return 'input'


class LinkSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = '__all__'

    def get_link(self, link):
        return get_link(link, self.context, 'link')

    def get_type(self, link):
        return 'link'


class CodeSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Code
        fields = '__all__'

    def get_link(self, code):
        return get_link(code, self.context, 'code')

    def get_type(self, code):
        return 'code'


class FileSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    teammates = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_link(self, file):
        return get_link(file, self.context, 'file')

    def get_teammates(self, file):
        if 'teammates' in self.context:
            cell_file_links = CellFileLink.objects.filter(file=file)

            if self.context['teammates'] == 'detail':
                return [link.cell.profile.name for link in cell_file_links]

            elif self.context['teammates'] == 'id':
                return [link.cell.profile.id for link in cell_file_links]

    def get_type(self, file):
        return 'file'


class CallSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = '__all__'

    def get_link(self, call):
        return get_link(call, self.context, 'call')

    def get_files(self, call):
        return get_children(call, self.context, 'call', 'file')

    def get_links(self, call):
        return get_children(call, self.context, 'call', 'link')

    def get_type(self, call):
        return 'call'


class DaySerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Day
        fields = '__all__'

    def get_tasks(self, day):
        return get_children(day, self.context, 'day', 'task')

    def get_notes(self, day):
        return get_children(day, self.context, 'day', 'note')

    def get_files(self, day):
        return get_children(day, self.context, 'day', 'file')

    def get_type(self, day):
        return 'day'


class CellSerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    calls = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Cell
        fields = '__all__'

    def get_tasks(self, cell):
        return get_children(cell, self.context, 'cell', 'task')

    def get_notes(self, cell):
        return get_children(cell, self.context, 'cell', 'note')

    def get_files(self, cell):
        return get_children(cell, self.context, 'cell', 'file')

    def get_calls(self, cell):
        return get_children(cell, self.context, 'cell', 'call')

    def get_type(self, cell):
        return 'cell'


class WorkSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    work_columns = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    shifts = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = '__all__'

    def get_link(self, work):
        return get_link(work, self.context, 'work')

    def get_apps(self, work):
        return get_children(work, self.context, 'work', 'app')

    def get_work_columns(self, work):
        return WorkColumnSerializer(work.columns.all(), many=True).data

    def get_files(self, work):
        return get_children(work, self.context, 'work', 'file')

    def get_shifts(self, work):
        return get_children(work, self.context, 'work', 'shift')

    def get_apps(self, work):
        if 'apps' in self.context:
            return [app.id for app in work.apps.all()]

    def get_type(self, work):
        return 'work'


class WorkColumnSerializer(serializers.ModelSerializer):

    rows = serializers.SerializerMethodField()

    class Meta:
        model = WorkColumn
        fields = '__all__'

    def get_rows(self, work_column):
        rows = work_column.rows.all()
        
        return WorkRowSerializer(rows, many=True).data


class WorkRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkRow
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):

    parts = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = '__all__'

    def get_parts(self, shift):
        return get_children(shift, self.context, 'shift', 'part')

    def get_type(self, shift):
        return 'shift'


class PartSerializer(serializers.ModelSerializer):

    profiles = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    work = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    teammates = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = '__all__'

    def get_profiles(self, part):
        return get_children(part, self.context, 'part', 'profile')

    def get_team(self, part):
        ctx = {'link': 'detail', 'profiles': 'detail'}

        return get_child(part, ctx, 'team')

    def get_work(self, part):
        return WorkSerializer(
            part.shift.work, context={'files': 'detail'}).data

    def get_shift(self, part):
        return get_child(part, None, 'shift')

    def get_project(self, part):
        project = get_child(part, None, 'project')

        try:
            if project['id']:
                return get_child(part, None, 'project')

        except KeyError:
            return None


    def get_teammates(self, part):
        teammates = list()

        if 'teammates' in self.context:
            work_parts = part.shift.part_set.all()

            for work_part in work_parts:
                links = PartProfileLink.objects.filter(part=work_part)

                for link in links:
                    if link.is_participant:
                        if self.context['teammates'] == 'detail':
                            teammates.append(link.profile.name)

                        elif self.context['teammates'] == 'id':
                            teammates.append(link.profile.id)

            return teammates

    def get_type(self, part):
        return 'part'


class PartSimpleSerializer(serializers.ModelSerializer):

    work = serializers.SerializerMethodField()
    teammates = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = '__all__'

    def get_work(self, part):
        return WorkSerializer(part.shift.work).data

    def get_shift(self, part):
        return get_child(part, None, 'shift')

    def get_teammates(self, part):
        teammates = list()

        if 'teammates' in self.context:
            work_parts = part.shift.part_set.all()

            for work_part in work_parts:
                links = PartProfileLink.objects.filter(part=work_part)

                for link in links:
                    if link.is_participant:
                        if self.context['teammates'] == 'detail':
                            teammates.append(link.profile.name)

                        elif self.context['teammates'] == 'id':
                            teammates.append(link.profile.id)

            return teammates

    def get_type(self, part):
        return 'part'


class QuotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quota
        fields = '__all__'


class LeaveConfigSerializer(serializers.ModelSerializer):

    leave_types = serializers.SerializerMethodField()

    class Meta:
        model = LeaveConfig
        fields = '__all__'

    def get_leave_types(self, config):
        return LeaveTypeSerializer(
            config.leave_type_set.all(), many=True).data


class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = '__all__'


class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    work = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_work(self, message):
        return get_child(message, {'shifts': 'detail'}, 'work')

    def get_author(self, message):
        return message.author.name


class LogSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = '__all__'

    def get_author(self, log):
        return log.profile.name


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #
# @@@@@@@@@@@@@@@@ Links Serializers @@@@@@@@@@@@@@@@ #
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #


class TeamProfileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamProfileLink
        fields = '__all__'


class AppWorkLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppWorkLink
        fields = '__all__'


class AppProjectLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppProjectLink
        fields = '__all__'


class AppFolderLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppFolderLink
        fields = '__all__'


class AppTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppTaskLink
        fields = '__all__'


class AppContactLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppContactLink
        fields = '__all__'


class DayTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayTaskLink
        fields = '__all__'


class DayNoteLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayNoteLink
        fields = '__all__'


class DayFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayFileLink
        fields = '__all__'


class CellTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellTaskLink
        fields = '__all__'


class CellNoteLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellNoteLink
        fields = '__all__'


class CellFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellFileLink
        fields = '__all__'


class CellCallLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellCallLink
        fields = '__all__'


class WorkFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkFileLink
        fields = '__all__'


class CallFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallFileLink
        fields = '__all__'


class CallLinkLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallLinkLink
        fields = '__all__'


class PartProfileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartProfileLink
        fields = '__all__'


class ProjectTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTaskLink
        fields = '__all__'


class AppTemplateLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppTemplateLink
        fields = '__all__'


class TaskSubtaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskSubtaskLink
        fields = '__all__'


class TaskNoteLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskNoteLink
        fields = '__all__'


class TaskFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskFileLink
        fields = '__all__'


class TaskInputLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskInputLink
        fields = '__all__'


class TaskLinkLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskLinkLink
        fields = '__all__'


class TaskCodeLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskCodeLink
        fields = '__all__'


class FolderTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = FolderTaskLink
        fields = '__all__'


class FolderNoteLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = FolderNoteLink
        fields = '__all__'


class FolderFileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = FolderFileLink
        fields = '__all__'


class FolderLinkLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = FolderLinkLink
        fields = '__all__'
