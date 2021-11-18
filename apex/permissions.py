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

    def get_element_from_set(self, parent, _type, _id):
        element_set = None

        try:
            element_set = getattr(parent, _type + 's')
        except AttributeError:
            element_set = getattr(parent, _type + '_set')

        return element_set.get(pk=_id)


class ElementHelpers(CommonHelpers):

    def get_data(self, request):
        data = self.parse_request_data(request)
        hierarchy = self.get_hierarchy(data)
        permission = self.get_permission(request, data, hierarchy['team'])

        return data, hierarchy, permission


    def parse_request_data(self, request):
        data = {
            'action': self.has_data(request, 'action'),
            'team_id': self.has_data(request, 'team_id'),
            'app_id': self.has_data(request, 'app_id'),
            'element_id': self.has_data(request, 'element_id'),
            'element_type': self.has_data(request, 'element_type'),
            'parent_type': self.has_data(request, 'parent_type'),
            'parent_id': self.has_data(request, 'parent_id'),
            'new_parent_type': self.has_data(request, 'new_parent_type'),
            'new_parent_id': self.has_data(request, 'new_parent_id'),
            'source_type': self.has_data(request, 'source_type'),
            'source_id': self.has_data(request, 'source_id'),
            'view': self.has_data(request, 'view'),
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


    def get_hierarchy(self, data):
        source = None
        source_set = None
        source_model = None
        source_serializer = None
        parent = None
        parent_set = None
        parent_model = None
        parent_serializer = None
        new_parent = None
        new_parent_model = None
        new_parent_serializer = None
        new_parent_set = None
        element = None
        element_model = None
        element_serializer = None
        link_model = None
        link_serializer = None

        team = Team.objects.get(pk=data['team_id'])
        app = team.app_set.get(pk=data['app_id'])


        if data['element_type']:
            element_model = globals()[data['element_type'].capitalize()]
            element_serializer = globals()[
                data['element_type'].capitalize() + 'Serializer']

        if data['source_type']:
            parent_model = globals()[data['parent_type'].capitalize()]
            parent_serializer = globals()[
                data['parent_type'].capitalize() + 'Serializer']
            source_model = globals()[data['source_type'].capitalize()]
            source_serializer = globals()[
                data['source_type'].capitalize() + 'Serializer']

        elif data['parent_type']:
            parent_model = globals()[data['parent_type'].capitalize()]
            parent_serializer = globals()[
                data['parent_type'].capitalize() + 'Serializer']
            source_model = parent_model
            source_serializer = parent_serializer

        if data['new_parent_type']:
            new_parent_model = globals()[data['new_parent_type'].capitalize()]
            new_parent_serializer = globals()[
                data['new_parent_type'].capitalize() + 'Serializer']

        if data['element_type'] and data['parent_type']:
            link_model = globals()[
                data['parent_type'].capitalize() +
                data['element_type'].capitalize() + 'Link']
            link_serializer = globals()[
                data['parent_type'].capitalize() +
                data['element_type'].capitalize() + 'LinkSerializer']


        # Override "app" if in Planner and parent is a Watcher day
        is_day = 'day' in [data['source_type'], data['parent_type']]

        if data['view'] == 'board' and is_day:
            find = [a for a in team.app_set.all() if a.app == 'watcher']
            app = None if not find else find[0]


        if data['source_id'] and data['source_type']:
            if data['source_type'] == 'cell':
                source = Cell.objects.get(pk=data['source_id'])
                profile = team.profiles.get(pk=source.profile.id)

            else:
                source = self.get_element_from_set(
                    app, data['source_type'], data['source_id'])

            source = self.get_element_from_set(
                source, data['parent_type'], data['parent_id'])

        elif data['parent_id'] and data['parent_type']:
            if data['parent_type'] == 'cell':
                source = Cell.objects.get(pk=data['parent_id'])
                profile = team.profiles.get(pk=source.profile.id)
                parent = source

            else:
                source = self.get_element_from_set(
                    app, data['parent_type'], data['parent_id'])
                parent = source


        if data['action'] in ['update', 'delete']:
            element_set = getattr(parent, data['element_type'] + 's')
            element = element_set.get(pk=data['element_id'])

        if data['action'] == 'position':
            if parent:
                element_set = getattr(parent, data['element_type'] + 's')
                element = element_set.get(pk=data['element_id']) 
            
            else:
                if data['element_type'] == 'cell':
                    element = Cell.objects.get(pk=data['element_id'])
                    profile = team.profiles.get(pk=element.profile.id)

                else:
                    element = self.get_element_from_set(
                        app, data['element_type'], data['element_id'])

            for child in data['position_updates']:
                child_set = getattr(element, child['element_type'] + 's')
                child = child_set.get(pk=child['element_id'])

        if data['action'] == 'move':
            element = self.get_element_from_set(
                parent, data['element_type'], data['element_id'])

            # Might break in other contexts than Planner's folders
            new_parent = self.get_element_from_set(
                app, data['new_parent_type'], data['new_parent_id'])


        return {
            'team': team,
            'app': app,
            'source': source,
            'source_model': source_model,
            'source_serializer': source_serializer,
            'parent': parent,
            'parent_model': parent_model,
            'parent_serializer': parent_serializer,
            'new_parent': new_parent,
            'new_parent_model': new_parent_model,
            'new_parent_serializer': new_parent_serializer,
            'element': element,
            'element_model': element_model,
            'element_serializer': element_serializer,
            'link_model': link_model,
            'link_serializer': link_serializer,
        }


    def get_permission(self, request, data, team):
        is_user = False
        is_editor = False

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        if access:
            views_app = {
                'board': 'planner',
                'calendar': 'watcher',
                'project': 'draft'
            }

            is_user = getattr(access, views_app[data['view']] + '_is_user')
            is_editor = getattr(access, views_app[data['view']] + '_is_editor')


        # Check access

        if data['action'] in ['create', 'delete', 'position', 'move']:
            return is_editor

        if data['action'] == 'update':
            possible_fields = ['name', 'key', 'value', 'heading']

            for field in possible_fields:
                if data[field]:
                  return is_editor

            if data['status']:
                return is_user