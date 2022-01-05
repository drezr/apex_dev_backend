from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class PresencesView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        date = request.query_params['date']

        team = Team.objects.get(pk=team_id)
        presences = list()

        for profile in team.profiles.all():
            cell, c = Cell.objects.get_or_create(
                profile_id=profile.id, date=date)

            presences.append({
                'profile_id': profile.id,
                'presence': cell.presence,
                'absence': cell.absence,
            })

        result = {
            'presences': presences,
        }

        return Response(result)