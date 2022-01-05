from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class HomeView(APIView):

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
                context={'teams': 'detail'}
            ).data,
            'user_teams': TeamSerializer(user_teams, many=True).data,
        }


        return Response(result)


    def post(self, request):
        if request.data['action'] == 'change_password':
            user_id = request.data['user_id']

            if user_id == request.user.id:
                current_password = request.data['current_password']
                new_password = request.data['new_password']
                new_password2 = request.data['new_password2']

                checked = check_password(
                    current_password, request.user.password)
                is_same = new_password == new_password2

                if checked:
                    if is_same:
                        if len(new_password) >= 8:
                            request.user.set_password(new_password)
                            request.user.save()

                            return Response({'result': 'success'})

                        else:
                            return Response({'result': 'length'})

                    else:
                        return Response({'result': 'not_same'})

                else:
                    return Response({'result': 'bad'})


        return Response(status=status.HTTP_400_BAD_REQUEST)