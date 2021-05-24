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

    def get(self, request):
        apps = App.objects.filter(team=request.query_params['team'])
        result = AppSerializer(apps, many=True).data

        return JsonResponse(result, safe=False)