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
        team_id = request.data['team_id']
        app_id = request.data['app_id']
        task_id = self.has_data(request, 'task_id')
        project_id = self.has_data(request, 'project_id')
        status = self.has_data(request, 'status')
        name = self.has_data(request, 'name')

        team = Team.objects.get(pk=team_id)
        app = team.app_set.get(pk=app_id)

        print(request.method)

        if project_id:
            project = app.project_set.get(pk=project_id)

            link = TeamProfileLink.objects.filter(
                team=team,
                profile=request.user.profile,
            )

            if request.method in ['PATCH', 'DELETE']:
                task = project.tasks.get(pk=task_id)

                if request.method == 'PATCH':
                    if name: return link[0].draft_is_editor
                    if status: return link[0].draft_is_user

                elif request.method == 'DELETE':
                    return link[0].draft_is_editor

            # if request.method == 'DELETE':
            #     return link[0].draft_is_editor

        return False