from copy import deepcopy

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

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

    class Meta:
        model = Profile
        fields = '__all__'

    def get_link(self, profile):
        return get_link(profile, self.context, 'profile')


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
    templates = serializers.SerializerMethodField()
    radium_config = serializers.SerializerMethodField()

    class Meta:
        model = App
        fields = '__all__'

    def get_projects(self, app):
        return get_children(app, self.context, 'app', 'project')

    def get_templates(self, app):
        return get_children(app, self.context, 'app', 'template')

    def get_radium_config(self, app):
        if 'radium_config' in self.context:
            radium_config = RadiumConfigSerializer(
                app.radiumconfig_set, many=True).data

            return None if not len(radium_config) else radium_config[0]


class RadiumConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = RadiumConfig
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_tasks(self, project):
        return get_children(project, self.context, 'project', 'task')

    def get_link(self, project):
        return get_link(project, self.context, 'project')


class TemplateSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    inputs = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = '__all__'

    def get_inputs(self, template):
        return get_children(template, self.context, 'template', 'input')

    def get_link(self, template):
        return get_link(template, self.context, 'template')


class TaskSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    subtasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    inputs = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

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

    def get_link(self, task):
        return get_link(task, self.context, 'task')


class SubtaskSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = Subtask
        fields = '__all__'

    def get_link(self, subtask):
        return get_link(subtask, self.context, 'subtask')


class NoteSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = '__all__'

    def get_link(self, note):
        return get_link(note, self.context, 'note')


class InputSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = Input
        fields = '__all__'

    def get_link(self, input):
        return get_link(input, self.context, 'input')


class LinkSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = '__all__'

    def get_link(self, link):
        return get_link(link, self.context, 'link')


class FileSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_link(self, file):
        return get_link(file, self.context, 'file')


class CallSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = '__all__'

    def get_link(self, call):
        return get_link(call, self.context, 'call')

    def get_files(self, call):
        return get_children(call, self.context, 'call', 'file')

    def get_links(self, call):
        return get_children(call, self.context, 'call', 'link')


class DaySerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Day
        fields = '__all__'

    def get_tasks(self, day):
        return get_children(day, self.context, 'day', 'task')

    def get_notes(self, day):
        return get_children(day, self.context, 'day', 'note')

    def get_files(self, day):
        return get_children(day, self.context, 'day', 'file')


class CellSerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    calls = serializers.SerializerMethodField()

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


class WorkSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    s460s = serializers.SerializerMethodField()
    limits = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    shifts = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = '__all__'

    def get_apps(self, work):
        return get_children(work, self.context, 'work', 'app')

    def get_s460s(self, work):
        return get_children(work, self.context, 'work', 's460')

    def get_limits(self, work):
        return get_children(work, self.context, 'work', 'limit')

    def get_files(self, work):
        return get_children(work, self.context, 'work', 'file')

    def get_shifts(self, work):
        return get_children(work, self.context, 'work', 'shift')

    def get_link(self, work):
        return get_link(work, self.context, 'work')


class LimitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Limit
        fields = '__all__'


class S460Serializer(serializers.ModelSerializer):

    class Meta:
        model = S460
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_link(self, work):
        return get_link(work, self.context, 'file')


class ShiftSerializer(serializers.ModelSerializer):

    parts = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = '__all__'

    def get_parts(self, work):
        return get_children(work, self.context, 'shift', 'part')


class PartSerializer(serializers.ModelSerializer):

    profiles = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    work = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = '__all__'

    def get_profiles(self, part):
        return get_children(part, self.context, 'part', 'profile')

    def get_team(self, part):
        ctx = {'link': 'detail', 'profiles': 'detail'}
        return get_child(part, ctx, 'team')

    def get_work(self, part):
        return get_child(part, None, 'work')

    def get_shift(self, part):
        return get_child(part, None, 'shift')

    def get_project(self, part):
        return get_child(part, None, 'project')


class LeaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leave
        fields = '__all__'


class RRSerializer(serializers.ModelSerializer):

    class Meta:
        model = RR
        fields = '__all__'


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


class AppTaskLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppTaskLink
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


class TemplateInputLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateInputLink
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
