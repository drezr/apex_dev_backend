from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class CalendarMobileView(APIView):

    def get(self, request):
        profile_id = request.query_params['profile_id']
        month = request.query_params['month']
        year = request.query_params['year']

        profile = Profile.objects.get(pk=profile_id)
        tp_link = TeamProfileLink.objects.filter(profile=profile).first()
        team = tp_link.team
        watcher = team.app_set.filter(app='watcher').first()

        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile=profile)

        holidays = Holiday.objects.filter(date__month=month, date__year=year)
        leave_config, lc = LeaveConfig.objects.get_or_create(app=watcher)

        result = {
            'cells': CellSerializer(cells, many=True).data,
            'leave_config': LeaveConfigSerializer(leave_config).data,
            'holidays': HolidaySerializer(holidays, many=True).data,
        }

        return Response(result)