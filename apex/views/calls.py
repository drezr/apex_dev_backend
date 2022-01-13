from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class CallsView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        profiles = [profile for profile in team.profiles.all()]
        visible_profiles = list()

        access = TeamProfileLink.objects.get(
            profile=request.user.profile, team=team)

        for profile in profiles:
            link = TeamProfileLink.objects.get(profile=profile, team=team)

            if link.watcher_is_visible:
                if access.watcher_can_see_cells or profile == request.user.profile:
                    visible_profiles.append(profile)

        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile__in=visible_profiles)

        calls = list()

        for cell in cells:
            for call in cell.calls.all():
                call = CallSerializer(call, context={
                    'files': 'detail',
                    'links': 'detail',
                }).data

                call['date'] = cell.date
                call['profile'] = ProfileSerializer(cell.profile).data
                calls.append(call)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'calls': calls,
        }

        return Response(result)