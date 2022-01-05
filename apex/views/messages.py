from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class MessagesView(APIView):

    def get(self, request):
        if 'app_id' in request.query_params:
            app_id = request.query_params['app_id']
            messages = Message.objects.filter(app=app_id).order_by('-date')

        result = {
            'messages': MessageSerializer(messages, many=True).data,
        }

        return Response(result)