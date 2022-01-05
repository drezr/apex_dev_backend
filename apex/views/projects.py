from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class ProjectsView(APIView, GenericHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']

        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(App.objects.get(pk=app_id), context={
                'link': 'detail',
                'projects': 'detail',
            }).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'create_project':
            project = Project.objects.create(
                name=data['value']['name'],
                date=data['value']['date'],
                private=data['value']['private'],
            )

            position = len(hierarchy['app'].project_set.all())

            app_project_link = AppProjectLink.objects.create(
                app=hierarchy['app'],
                project=project,
                position=position,
            )

            project_serialized = ProjectSerializer(project).data
            project_serialized['link'] = AppProjectLinkSerializer(
                app_project_link).data

            return Response({'project': project_serialized})


        elif data['action'] == 'update_project':
            project = Project.objects.get(pk=data['element_id'])

            for arg in ['name', 'date', 'private', 'archived']:
                setattr(project, arg, data['value'][arg])

            project.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_project_position':
            for pu in data['position_updates']:
                project = Project.objects.get(pk=pu['project_id'])
                link = AppProjectLink.objects.get(
                    app=hierarchy['app'],
                    project=project,
                )

                link.position = pu['position']
                link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_project':
            app = hierarchy['app']
            project = Project.objects.get(pk=data['element_id'])

            for task in project.tasks.all():
                for child_type in ['note', 'subtask', 'input', 'file']:
                    child_set = getattr(task, child_type + 's')
                    
                    for child in child_set.all():
                        if child_type == 'file':
                            # TODO : file stuff
                            pass

                        child.delete()

                task.delete()

            project.delete()

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)