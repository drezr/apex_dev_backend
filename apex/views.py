from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *


class HomeView(APIView):

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


class TeamView(APIView):

    def get(self, request, team_id):
        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'apps': 'detail'
            }).data,
        }

        return Response(result)


class DraftView(APIView):

    def get(self, request, team_id, app_id):
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


class TemplateView(APIView):

    def get(self, request, team_id, app_id):
        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(App.objects.get(pk=app_id), context={
                'link': 'detail',
                'templates': 'detail',
                'inputs': 'detail',
            }).data,
        }

        return Response(result)


class ProjectView(APIView):

    def get(self, request, team_id, app_id, project_id):
        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)
        project = Project.objects.get(pk=project_id)

        result = {
            'team': TeamSerializer(team).data,
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

        return Response(result)


class CalendarView(APIView):

    def get(self, request, team_id, app_id):
        app = App.objects.get(pk=app_id)
        app = AppSerializer(app, context={
            'link': 'detail',
            'profiles': 'detail',
        }).data

        return Response(app)
