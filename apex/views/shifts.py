from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class ShiftsView(APIView):

    def get(self, request):
        work_id = request.query_params['work_id']

        shifts = Shift.objects.filter(work=work_id)

        result = {
            'shifts': ShiftSerializer(shifts, context={
                'link': 'detail',
                'parts': 'detail',
                'profiles': 'detail',
                'project': 'detail',
            }, many=True).data,
        }

        return Response(result)