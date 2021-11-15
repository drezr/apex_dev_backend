from rest_framework import permissions

from .models import *
from .serializers import *


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class CommonHelpers:

    def has_param(self, request, param):
        if param in request.query_params:
            return request.query_params[param]

        return None


    def has_data(self, request, data):
        if data in request.data:
            return request.data[data]

        return None


    def get_objects(self, data):
        element = None
        model = None
        serializer = None

        if data['type']:
            model = globals()[data['type'].capitalize()]
            serializer = globals()[data['type'].capitalize() + 'Serializer']

            if data['element_id']:
                element = model.objects.get(pk=data['element_id'])

        return element, model, serializer


class ElementHelpers(CommonHelpers):

    def get_data(self, request):
        data = self.parse_request_data(request)
        element, model, serializer = self.get_objects(data)
        permission = self.get_permission(
            request, data, element, model, serializer)

        return data, element, model, serializer, permission


    def parse_request_data(self, request):
        data = {
            'action': self.has_data(request, 'action'),
            'team_id': self.has_data(request, 'team_id'),
            'app_id': self.has_data(request, 'app_id'),
            'project_id': self.has_data(request, 'project_id'),
            'day_cell_id': self.has_data(request, 'day_cell_id'),
            'folder_id': self.has_data(request, 'folder_id'),
            'task_id': self.has_data(request, 'task_id'),
            'element_id': self.has_data(request, 'element_id'),
            'source_type': self.has_data(request, 'source_type'),
            'view': self.has_data(request, 'view'),
            'type': self.has_data(request, 'type'),
            'kind': self.has_data(request, 'kind'),
            'status': self.has_data(request, 'status'),
            'name': self.has_data(request, 'name'),
            'key': self.has_data(request, 'key'),
            'value': self.has_data(request, 'value'),
            'heading': self.has_data(request, 'heading'),
            'start': self.has_data(request, 'start'),
            'end': self.has_data(request, 'end'),
            'description': self.has_data(request, 'description'),
            'position_updates': self.has_data(request, 'position_updates'),
        }

        return data


    def get_permission(self, request, data, element, model, serializer):
        team = Team.objects.get(pk=data['team_id'])
        app = team.app_set.get(pk=data['app_id'])

        team_links = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        )

        access = None

        if len(team_links) == 1:
            access = team_links[0]

        else:
            print('Warning: more than 1 team profile link !')

            return False

        if data['view'] == 'project':
            return self.get_draft_permission(data, app, access)

        elif data['view'] == 'calendar':
            return self.get_planner_watcher_permission(data, app, access)

        elif data['view'] == 'board':
            return self.get_planner_watcher_permission(data, app, access)

        return False


    def get_planner_watcher_permission(self, data, app, access):
        parent = None
        is_editor = None
        is_user = None

        if data['view'] == 'calendar':
            is_editor = access.watcher_is_editor
            is_user = access.watcher_is_user

        elif data['view'] == 'board':
            is_editor = access.planner_is_editor
            is_user = access.planner_is_user


        if data['source_type'] == 'day':
            if data['view'] == 'board':
                for _app in app.team.app_set.all():
                    if _app.app == 'watcher':
                        parent = _app.day_set.get(pk=data['day_cell_id'])
                        break

            elif data['view'] == 'calendar':
                parent = app.day_set.get(pk=data['day_cell_id'])

        elif data['source_type'] == 'cell':
            parent = Cell.objects.get(pk=data['day_cell_id'])
            app.team.profiles.get(pk=parent.profile.id)

        elif data['source_type'] == 'folder':
            parent = Folder.objects.get(pk=data['folder_id'])
            element_set = getattr(parent, data['type'] + 's')
            element_set.get(pk=data['element_id'])


        if data['action'] in ['update', 'delete']:
            if data['task_id']:
                task = parent.tasks.get(pk=data['task_id'])
                element_set = getattr(task, data['type'] + 's')
                element_set.get(pk=data['element_id'])

            else:
                element_set = getattr(parent, data['type'] + 's')
                element_set.get(pk=data['element_id'])


        possible_fields = ['name', 'key', 'value', 'heading']

        if data['action'] == 'update':
            for field in possible_fields:
                if data[field]:
                  return is_editor

            if data['status']:
                return is_user

        elif data['action'] == 'create':
            return is_editor

        elif data['action'] == 'delete':
            return is_editor


        return False


    def get_draft_permission(self, data, app, access):
        project = app.project_set.get(pk=data['project_id'])

        if data['action'] == 'position':
            if not data['task_id']:
                for element_data in data['position_updates']:
                    task = project.tasks.get(pk=element_data['element_id'])

            else:
                task = project.tasks.get(pk=data['task_id'])

                for element_data in data['position_updates']:
                    element_set = getattr(task, element_data['type'] + 's')
                    element_set.get(pk=element_data['element_id'])

            return access.draft_is_editor


        elif data['action'] in ['update', 'delete']:
            if data['type'] == 'task':
                task = project.tasks.get(pk=data['element_id'])

            else:
                task = project.tasks.get(pk=data['task_id'])
                element_set = getattr(task, data['type'] + 's')
                element_set.get(pk=data['element_id'])

            possible_fields = ['name', 'key', 'value', 'heading']

            if data['action'] == 'update':
                for field in possible_fields:
                    if data[field]:
                      return access.draft_is_editor  

                if data['status']:
                    return access.draft_is_user

            elif data['action'] == 'delete':
                return access.draft_is_editor

        elif data['action'] == 'create':
            return access.draft_is_editor

        else:
            return False