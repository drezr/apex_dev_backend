from rest_framework import permissions

from .models import *
from .serializers import *

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

        if data['kind']:
            model = globals()[data['kind'].capitalize()]
            serializer = globals()[data['kind'].capitalize() + 'Serializer']

            if data['element_id']:
                element = model.objects.get(pk=data['element_id'])

        return element, model, serializer



class ElementHelpers(CommonHelpers):

    def parse_request_data(self, request):
        data = {
            'action': self.has_data(request, 'action'),
            'team_id': self.has_data(request, 'team_id'),
            'app_id': self.has_data(request, 'app_id'),
            'project_id': self.has_data(request, 'project_id'),
            'task_id': self.has_data(request, 'element_id'),
            'element_id': self.has_data(request, 'element_id'),
            'kind': self.has_data(request, 'kind'),
            'status': self.has_data(request, 'status'),
            'name': self.has_data(request, 'name'),
            'key': self.has_data(request, 'key'),
            'value': self.has_data(request, 'value'),
            'heading': self.has_data(request, 'heading'),
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

        if data['project_id']:
            project = app.project_set.get(pk=data['project_id'])

            if data['action'] in ['update', 'position', 'delete']:
                if data['kind'] == 'task':
                    task = project.tasks.get(pk=data['element_id'])

                else:
                    task = project.tasks.get(pk=data['task_id'])
                    element_set = getattr(task, data['kind'] + 's')
                    element_set.get(pk=element['element_id'])

                if data['action'] == 'update':
                    possible_fields = ['name', 'key', 'value', 'heading']

                    for field in possible_fields:
                        if data[field]:
                          return access.draft_is_editor  

                    if data['status']:
                        return access.draft_is_user

                elif data['action'] in ['position', 'delete']:
                    return access.draft_is_editor

            elif data['action'] == 'create':
                return access.draft_is_editor

        return False

    def get_data(self, request):
        data = self.parse_request_data(request)
        element, model, serializer = self.get_objects(data)
        permission = self.get_permission(
            request, data, element, model, serializer)

        return data, element, model, serializer, permission


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser