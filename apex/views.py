from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *


class Home(APIView):

    def get(self, request):
        circles = Circle.objects.all()
        profile = request.user.profile

        user_teams = list()

        for circle in circles:
            teams = circle.team_set.filter(profiles__in=[profile])
            [user_teams.append(team) for team in teams]

        result = {
            'circles': CircleSerializer(
                circles, many=True,
                context={'teams': 'detail'}
            ).data,
            'user_teams': TeamSerializer(user_teams, many=True).data,
        }

        return Response(result)


class Hub(APIView):

    def get(self, request, team_id):
        team = Team.objects.get(pk=team_id)
        result = TeamSerializer(team, context={'apps': 'detail'}).data

        return Response(result)


class Draft(APIView):

    def get(self, request, app_id):
        app = App.objects.get(pk=app_id)
        app = AppSerializer(app, context={
            'link': 'detail',
            'projects': 'detail',
        }).data

        return Response(app)


class ProjectView(APIView):

    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        project = ProjectSerializer(project, context={
            'link': 'detail',
            'tasks': 'detail',
            'subtasks': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'inputs': 'detail',
        }).data

        return Response(project)


class TemplateView(APIView):

    def get(self, request, app_id):
        app = App.objects.get(pk=app_id)
        app = AppSerializer(app, context={
            'link': 'detail',
            'templates': 'detail',
            'inputs': 'detail',
        }).data

        return Response(app)
