from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class MyApexView(APIView):

    def get(self, request):
        result = {
            'profile': ProfileSerializer(request.user.profile, context={
                'apps': 'detail',
            }).data,
        }

        return Response(result)