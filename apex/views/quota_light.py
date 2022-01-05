from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *

from ..quota import compute_quota


class QuotaLightView(APIView):

    def get(self, request):
        end = request.query_params['end']
        app_id = request.query_params['app_id']
        profile_id = request.query_params['profile_id']
        month = request.query_params['month']
        year = request.query_params['year']

        holidays = Holiday.objects.filter(date__year=year)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

        for leave_type in config.leave_type_set.all():
            if leave_type.visible:
                Quota.objects.get_or_create(
                    code=leave_type.code,
                    year=year,
                    profile_id=profile_id,
                )


        quotas = Quota.objects.filter(profile=profile_id, year=year)

        end_quota_cells = None

        if end == 'month_start':
            end_quota_cells = Cell.objects.filter(
                date__month__lt=month,
                date__year=year,
                profile=profile_id,
            )

        elif end == 'month_end':
            end_quota_cells = Cell.objects.filter(
                date__month__lte=month,
                date__year=year,
                profile=profile_id,
            )

        elif end == 'year_end':
            end_quota_cells = Cell.objects.filter(
                date__month__lte=12,
                date__year=year,
                profile=profile_id,
            )

        base_quotas, computed_quotas, detailed_quotas = compute_quota(
            cells=CellSerializer(end_quota_cells, many=True).data,
            quotas=QuotaSerializer(quotas, many=True).data,
            config=LeaveConfigSerializer(config).data,
            holidays=HolidaySerializer(holidays, many=True).data,
            detailed=False
        )

        result = {
            'quota': computed_quotas,
        }

        return Response(result)