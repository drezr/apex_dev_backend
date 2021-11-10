from rest_framework import permissions

from .models import *


class PermissionHelpers(permissions.BasePermission):

    def has_param(self, request, param):
        if param in request.query_params:
            return request.query_params[param]

        return None

    def has_data(self, request, data):
        if data in request.data:
            return request.data[data]

        return None


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class TaskPermissions(PermissionHelpers):

    def has_permission(self, request, view):
        action = self.has_data(request, 'action')
        team_id = self.has_data(request, 'team_id')
        app_id = self.has_data(request, 'app_id')
        task_id = self.has_data(request, 'task_id')
        project_id = self.has_data(request, 'project_id')
        status = self.has_data(request, 'status')
        name = self.has_data(request, 'name')

        team = Team.objects.get(pk=team_id)
        app = team.app_set.get(pk=app_id)

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

        if project_id:
            project = app.project_set.get(pk=project_id)

            if action in ['update', 'delete']:
                task = project.tasks.get(pk=task_id)

                if action == 'update':
                    if name: return access.draft_is_editor
                    if status: return access.draft_is_user

                elif action == 'delete':
                    return access.draft_is_editor

        return False