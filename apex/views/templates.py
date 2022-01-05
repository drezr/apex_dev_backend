from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class TemplatesView(APIView, GenericHelpers):

    def get(self, request):
        app_id = request.query_params['app_id']

        result = {
            'app': AppSerializer(App.objects.get(pk=app_id), context={
                'link': 'detail',
                'tasks': 'detail',
                'inputs': 'detail',
                'notes': 'detail',
                'subtasks': 'detail',
            }).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'select_template':
            hierarchy['app'].template_id = data['value']
            hierarchy['app'].save()

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)