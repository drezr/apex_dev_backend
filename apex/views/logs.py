from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class LogsView(APIView):

    def get(self, request):
        if 'cell_id' in request.query_params:
            cell_id = request.query_params['cell_id']
            logs = Log.objects.filter(cell=cell_id).order_by('-date')

        elif 'work_id' in request.query_params:
            work_id = request.query_params['work_id']
            field = request.query_params['field']
            logs = Log.objects.filter(
                work=work_id, field=field).order_by('-date')

        result = {
            'logs': LogSerializer(logs, many=True).data,
        }

        return Response(result)