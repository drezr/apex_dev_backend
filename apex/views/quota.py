from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *

from ..quota import compute_quota


class QuotaView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        profile_id = request.query_params['profile_id']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)
        profile = Profile.objects.get(pk=profile_id)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

        for leave_type in config.leave_type_set.all():
            if leave_type.visible:
                Quota.objects.get_or_create(
                    code=leave_type.code,
                    year=year,
                    profile_id=profile_id,
                )

        quotas = Quota.objects.filter(
            profile=profile_id, year=year)
        cells = Cell.objects.filter(
            date__year=year, profile=profile_id)
        holidays = Holiday.objects.filter(date__year=year)


        base_quotas, computed_quotas, detailed_quotas = compute_quota(
            cells=CellSerializer(cells, many=True).data,
            quotas=QuotaSerializer(quotas, many=True).data,
            config=LeaveConfigSerializer(config).data,
            holidays=HolidaySerializer(holidays, many=True).data,
            detailed=True
        )

        result = {
            'team': TeamSerializer(team).data,
            'app': AppSerializer(app).data,
            'config': LeaveConfigSerializer(config).data,
            'profile': ProfileSerializer(profile).data,
            'base_quotas': base_quotas,
            'computed_quotas': computed_quotas,
            'detailed_quotas': detailed_quotas,
        }

        return Response(result)