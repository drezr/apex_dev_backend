from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class ProfileView(APIView):

    def get(self, request):
        username = request.query_params['username']
        user = User.objects.filter(username=username).first()

        if not user or request.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        result = {
            'profile': ProfileSerializer(user.profile, context={
                'user': 'detail'
            }).data,
        }

        return Response(result)