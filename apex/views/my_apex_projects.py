from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class MyApexProjectsView(APIView):

    def get(self, request):
        app_id = request.query_params['app_id']

        app = AppSerializer(App.objects.get(pk=app_id), context={
            'link': 'detail',
            'projects': 'detail',
        }).data

        if app['profile'] == request.user.profile.id:
            return Response({'app': app})

        return Response('Not Allowed')