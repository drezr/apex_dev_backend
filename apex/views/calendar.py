from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class CalendarView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)


        profiles_id = []

        user_access = TeamProfileLink.objects.filter(
            team_id=team_id,
            profile=request.user.profile,
        )

        if user_access.count() > 0:
            if user_access[0].watcher_can_see_cells:
                profiles_id = [profile.id for profile in team.profiles.all()]

            else:
                profiles_id = [request.user.profile.id]

        else:
            if request.user.profile.can_see_calendars:
                profiles_id = [profile.id for profile in team.profiles.all()]


        days = Day.objects.filter(
            date__month=month, date__year=year, team=team)
        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile__in=profiles_id)
        holidays = Holiday.objects.filter(date__month=month, date__year=year)

        leave_config, lc = LeaveConfig.objects.get_or_create(app_id=app_id)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'days': DaySerializer(days, many=True).data,
            'cells': CellSerializer(cells, many=True).data,
            'holidays': HolidaySerializer(holidays, many=True).data,
            'leave_config': LeaveConfigSerializer(leave_config).data,
        }

        return Response(result)