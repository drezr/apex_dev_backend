from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


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

            if project.private:
                link = TeamProfileLink.objects.get(
                    profile=request.user.profile, team=team)

                if not link.draft_can_see_private:
                    overrided_result = {'project': {'private': True}}
                    overrided_result['team'] = result['team']

                    return Response(overrided_result)

        return Response(result)