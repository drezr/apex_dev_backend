from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class ContactsView(APIView):

    def get(self, request):
        app_id = request.query_params['app_id']
        day = request.query_params['day']
        month = request.query_params['month']
        year = request.query_params['year']

        app = AppSerializer(App.objects.get(pk=app_id), context={
            'contacts': 'detail',
            'parent_id': app_id,
            'parent_type': 'app',
            'link': 'detail',
        }).data

        for contact in app['contacts']:
            cells = Cell.objects.filter(
                date__day=day,
                date__month=month,
                date__year=year,
                profile=contact['id']
            )

            if len(cells) == 1:
                contact['presence'] = cells[0].presence
                contact['absence'] = cells[0].absence

            elif len(cells) == 0:
                contact['presence'] = ''
                contact['absence'] = ''

            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        result = {
            'app': app,
        }

        return Response(result)