from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class AppsView(APIView):

    def get(self, request):
        circles = Circle.objects.all()
        profile = request.user.profile

        user_teams = list()
        user_circles = list()

        for circle in circles:
            teams = circle.team_set.filter(profiles__in=[profile])
            [user_teams.append(team) for team in teams]

            for team in user_teams:
                if len(circle.team_set.filter(pk=team.id)):
                    if circle not in user_circles:
                        user_circles.append(circle)


        result = {
            'circles': CircleSerializer(
                user_circles, many=True,
                context={'teams': 'detail', 'apps': 'detail'}
            ).data,
        }

        return Response(result)