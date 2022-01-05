from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class ProjectView(APIView):

    def get(self, request):
        app_id = request.query_params['app_id']
        project_id = request.query_params['project_id']
        
        app = App.objects.get(pk=app_id)
        project = Project.objects.get(pk=project_id)

        result = {
            'app': AppSerializer(app).data,
            'project': ProjectSerializer(project, context={
                'link': 'detail',
                'tasks': 'detail',
                'subtasks': 'detail',
                'notes': 'detail',
                'files': 'detail',
                'inputs': 'detail',
            }).data,
        }

        if 'team_id' in request.query_params:
            team_id = request.query_params['team_id']
            team = Team.objects.get(pk=team_id)

            result['team'] = TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data

        return Response(result)