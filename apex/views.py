from django.http import JsonResponse
from rest_framework.views import APIView

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

        return JsonResponse(result, safe=False)


class Hub(APIView):

    def get(self, request, team_id):
        apps = App.objects.filter(team=team_id)
        result = AppSerializer(apps, many=True).data

        return JsonResponse(result, safe=False)


class Draft(APIView):

    def get(self, request, app_id):
        projects = Project.objects.filter(apps__in=[app_id])
        projects = ProjectSerializer(projects, many=True).data

        return JsonResponse(projects, safe=False)



class ProjectView(APIView):

    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        project = ProjectSerializer(project, context={
            'tasks': 'detail',
            'subtasks': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'fields': 'detail',
        }).data

        return JsonResponse(project, safe=False)
