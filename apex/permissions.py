from rest_framework import permissions

from .models import *
from .serializers import *


class Helpers:

    def day_has_child(self, team, day):
        has_child = False

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(day, child_type + 's')

            if len(child_set.all()) > 0:
                has_child = True
                break

        if not has_child:
            parts = Part.objects.filter(team=team, date=day.date)

            if len(parts) > 0:
                has_child = True

        return has_child


    def cell_has_child(self, profile, cell):
        has_child = False

        parts = Part.objects.filter(
            profiles__in=[profile.id],
            date=cell.date,
        )

        for part in parts:
            for _profile in part.profiles.all():
                if _profile == profile:
                    _link = PartProfileLink.objects.get(
                        part=part,
                        profile=profile,
                    )

                    if _link.is_participant:
                        has_child = True
                        break

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(cell, child_type + 's')

            if len(child_set.all()) > 0:
                has_child = True
                break

        return has_child


    def cell_child_count(self, profile, cell):
        count = 0

        parts = Part.objects.filter(
            profiles__in=[profile.id],
            date=cell.date,
        )

        for part in parts:
            for _profile in part.profiles.all():
                if _profile == profile:
                    _link = PartProfileLink.objects.get(
                        part=part,
                        profile=profile,
                    )

                    if _link.is_participant:
                        count +=1

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(cell, child_type + 's')
            child_set_count = len(child_set.all())

            if child_set_count > 0:
                count += child_set_count

        return count


    def set_day_cells_has_content(self, team, profiles, date):
        day, d = Day.objects.get_or_create(team=team, date=date)
        has_child = self.day_has_child(team, day)

        day.has_content = has_child
        day.save()

        for profile in profiles:
            cell, c = Cell.objects.get_or_create(
                profile=profile, date=date)

            has_child = self.cell_has_child(
                cell.profile, cell)

            cell.has_content = has_child
            cell.save()


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
            'new_parent_date': self.has_data(request, 'new_parent_date'),
            'source_type': self.has_data(request, 'source_type'),
            'source_id': self.has_data(request, 'source_id'),
            'profile_id': self.has_data(request, 'profile_id'),
            'view': self.has_data(request, 'view'),
            'kind': self.has_data(request, 'kind'),
            'status': self.has_data(request, 'status'),
            'name': self.has_data(request, 'name'),
            'key': self.has_data(request, 'key'),
            'value': self.has_data(request, 'value'),
            'url': self.has_data(request, 'url'),
            'heading': self.has_data(request, 'heading'),
            'start': self.has_data(request, 'start'),
            'end': self.has_data(request, 'end'),
            'description': self.has_data(request, 'description'),
            'presence': self.has_data(request, 'presence'),
            'absence': self.has_data(request, 'absence'),
            'color': self.has_data(request, 'color'),
            'presence_color': self.has_data(request, 'presence_color'),
            'absence_color': self.has_data(request, 'absence_color'),
            'short': self.has_data(request, 'short'),
            'date': self.has_data(request, 'date'),
            'year': self.has_data(request, 'year'),
            'hour': self.has_data(request, 'hour'),
            'work': self.has_data(request, 'work'),
            'place': self.has_data(request, 'place'),
            'project': self.has_data(request, 'project'),
            'other': self.has_data(request, 'other'),
            'network': self.has_data(request, 'network'),
            'activity': self.has_data(request, 'activity'),
            'position_updates': self.has_data(request, 'position_updates'),
        }

        return data


    def get_data(self, request):
        data = self.parse_request_data(request)
        hierarchy = self.get_hierarchy(data)
        permission = self.get_permission(request, data, hierarchy['team'])

        return data, hierarchy, permission


class GenericHelpers(CommonHelpers):

    def get_hierarchy(self, data):
        hierarchy = dict()

        team = Team.objects.get(pk=data['team_id'])
        hierarchy['team'] = team

        if data['app_id']:
            app = team.app_set.get(pk=data['app_id'])
            hierarchy['app'] = app

        return hierarchy


    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        return access.is_manager if access else False


class BoardHelpers(CommonHelpers):

    def get_hierarchy(self, data):
        team = Team.objects.get(pk=data['team_id'])
        app = team.app_set.get(pk=data['app_id'])
        _data = {'team': team, 'app': app}

        if data['action'] == 'update_element_teammates':
            _data['profile'] = team.profiles.filter(pk=data['profile_id']).first()

            if not _data['profile']:
                _data['profile'] = Profile.objects.get(pk=data['profile_id'])

            _data['parent'] = team.day_set.get(pk=data['parent_id'])

            element_set = getattr(_data['parent'], data['element_type'] + 's')
            _data['element'] = element_set.get(pk=data['element_id'])

            _data['link_model'] = globals()[
                'Cell' + data['element_type'].capitalize() + 'Link']


        elif data['action'] == 'update_part_teammates':
            _data['profile'] = team.profiles.get(pk=data['profile_id'])
            _data['parent'] = Part.objects.get(pk=data['element_id'])

        return _data


    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        return access.planner_is_editor if access else False


class WorksHelpers(CommonHelpers):

    def get_hierarchy(self, data):
        team = Team.objects.get(pk=data['team_id'])
        app = team.app_set.get(pk=data['app_id'])

        source = None
        parent = None
        element = None

        if data['source_type'] and data['source_id']:
            if data['source_type'] == 'work':
                source = app.work_set.get(pk=data['source_id'])

        if data['parent_type'] and data['parent_id']:
            if data['parent_type'] == 'work':
                parent = app.work_set.get(pk=data['parent_id'])

            if data['parent_type'] == 'shift':
                parent = source.shift_set.get(pk=data['parent_id'])

        if data['element_type'] and data['element_id']:
            if data['element_type'] == 'work':
                if data['action'] != 'copy_work':
                    element = app.work_set.get(pk=data['element_id'])

            elif data['element_type'] == 'shift':
                child_set = getattr(parent, data['element_type'] + '_set')
                element = child_set.get(pk=data['element_id'])

            elif data['element_type'] == 'file':
                child_set = getattr(parent, data['element_type'] + 's')
                element = child_set.get(pk=data['element_id'])

            elif data['element_type'] == 'part':
                element = parent.part_set.get(pk=data['element_id'])

        return {
            'team': team,
            'app': app,
            'source': source,
            'parent': parent,
            'element': element,
        }

    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        if data['action'] == 'update_config':
            return access.radium_is_editor if access else False


        elif data['action'] in ['update_part_profile_link', 'create_part_profile_link']:
            if access.is_manager or access.radium_is_editor:
                return True

            else:
                profile = Profile.objects.get(pk=data['profile_id'])

                if profile.id == request.user.profile.id:
                    return True

                else:
                    return False

            return False

        else:
            return False if not access else access.radium_is_editor


class LeaveHelpers(CommonHelpers):

    def get_hierarchy(self, data):
        team = Team.objects.get(pk=data['team_id'])
        app = team.app_set.get(pk=data['app_id'])
        _data = {'team': team, 'app': app}

        if data['action'] == 'update_leave':
            _data['profile'] = team.profiles.get(pk=data['profile_id'])

        return _data

    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        return access.is_manager if access else False


class CellHelpers(CommonHelpers):

    def get_hierarchy(self, data):
        team = Team.objects.get(pk=data['team_id'])
        profile = team.profiles.get(pk=data['profile_id'])
        cell = profile.cell_set.get(pk=data['element_id'])

        return {
            'team': team,
            'profile': profile,
            'cell': cell,
        }

    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

        access = TeamProfileLink.objects.filter(
            team=team,
            profile=request.user.profile,
        ).first()

        return access.watcher_is_editor if access else False 


class ElementHelpers(CommonHelpers):

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
        new_link_model = None
        new_link_serializer = None

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

        if data['element_type'] and data['new_parent_type']:
            new_link_model = globals()[
                data['new_parent_type'].capitalize() +
                data['element_type'].capitalize() + 'Link']
            new_link_serializer = globals()[
                data['new_parent_type'].capitalize() +
                data['element_type'].capitalize() + 'LinkSerializer']


        if data['source_id'] and data['source_type']:
            if data['source_type'] == 'day':
                source = self.get_element_from_set(
                    team, data['source_type'], data['source_id'])

            elif data['source_type'] == 'cell':
                source = Cell.objects.get(pk=data['source_id'])
                profile = team.profiles.get(pk=source.profile.id)

            elif data['source_type'] == 'app':
                source = app

            else:
                source = self.get_element_from_set(
                    app, data['source_type'], data['source_id'])

            parent = self.get_element_from_set(
                source, data['parent_type'], data['parent_id'])

        elif data['parent_id'] and data['parent_type']:
            if data['parent_type'] == 'day':
                source = self.get_element_from_set(
                    team, data['parent_type'], data['parent_id'])
                parent = source

            elif data['parent_type'] == 'cell':
                source = Cell.objects.get(pk=data['parent_id'])
                profile = team.profiles.get(pk=source.profile.id)
                parent = source

            elif data['parent_type'] == 'app':
                parent = app

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
                if data['element_type'] == 'day':
                    element = self.get_element_from_set(
                        team, data['element_type'], data['element_id'])

                elif data['element_type'] == 'cell':
                    element = Cell.objects.get(pk=data['element_id'])
                    profile = team.profiles.get(pk=element.profile.id)

                else:
                    element = self.get_element_from_set(
                        app, data['element_type'], data['element_id'])

            for child in data['position_updates']:
                child_set = getattr(element, child['element_type'] + 's')
                child = child_set.get(pk=child['element_id'])

        if data['action'] == 'move':
            if data['new_parent_type'] == 'day':
                element = self.get_element_from_set(
                    parent, data['element_type'], data['element_id'])
                date = data['new_parent_date']
                new_parent, c = Day.objects.get_or_create(team=team, date=date)

            elif data['new_parent_type'] == 'cell':
                element = self.get_element_from_set(
                    parent, data['element_type'], data['element_id'])
                date = data['new_parent_date']
                new_parent = Cell.objects.get(pk=data['new_parent_id'])

            else:
                element = self.get_element_from_set(
                    parent, data['element_type'], data['element_id'])

                new_parent = self.get_element_from_set(
                        app, data['new_parent_type'], data['new_parent_id'])


        if data['action'] == 'copy':
            if data['new_parent_type'] == 'day':
                date = data['new_parent_date']
                new_parent, c = Day.objects.get_or_create(team=team, date=date)

            elif data['new_parent_type'] == 'cell':
                new_parent = Cell.objects.get(pk=data['new_parent_id'])

            else:
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
            'new_link_model': new_link_model,
            'new_link_serializer': new_link_serializer,
        }


    def get_permission(self, request, data, team):
        if request.user.is_staff:
            return True

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

        if data['action'] in ['create', 'delete', 'position', 'move', 'copy']:
            return is_editor

        if data['action'] == 'update':
            possible_fields = ['name', 'key', 'value', 'heading', 'url']

            for field in possible_fields:
                if data[field] != None:
                  return is_editor

            if data['status']:
                return is_user

        return False