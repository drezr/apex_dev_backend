import copy

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class CellView(APIView, CellHelpers):

    def get(self, request):
        profile_id = request.query_params['profile_id']
        date = request.query_params['date']

        cell, c = Cell.objects.get_or_create(profile_id=profile_id, date=date)

        cell = CellSerializer(cell, context={
            'link': 'detail',
            'tasks': 'detail',
            'subtasks': 'detail',
            'inputs': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'calls': 'detail',
            'links': 'detail',
            'codes': 'detail',
            'teammates': 'detail',
        }).data

        parts = Part.objects.filter(profiles__in=[profile_id], date=date)
        parts = PartSerializer(parts, many=True, context={
            'link': 'detail',
            'profiles': 'detail',
            'teammates': 'detail',
        }).data

        cell['parts'] = list()

        for part in parts:
            for profile in part['profiles']:
                if profile['link']['is_participant']:
                    if profile['id'] == int(profile_id):
                        cell['parts'].append(part)

        return Response({'cell': cell})


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        # Check for cell duplication
        cell_duplicates = Cell.objects.filter(
            profile=hierarchy['profile'],
            date=hierarchy['cell'].date,
        )

        if len(cell_duplicates) > 1:
            for _cell in cell_duplicates:
                if _cell.id != hierarchy['cell'].id:
                    _cell.delete()

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if data['action'] == 'update':
            old_presence = copy.deepcopy(hierarchy['cell'].presence)
            old_absence = copy.deepcopy(hierarchy['cell'].absence)

            hierarchy['cell'].presence = data['presence']
            hierarchy['cell'].absence = data['absence']
            hierarchy['cell'].color = data['color']
            hierarchy['cell'].presence_color = data['presence_color']
            hierarchy['cell'].absence_color = data['absence_color']
            hierarchy['cell'].short = data['short']

            hierarchy['cell'].save()


            if old_presence != data['presence'] or old_absence != data['absence']:
                def gs(presence, absence):
                    def fs(string):
                        return '-' if not string else string.upper()

                    return '{0} &#%$ {1}'.format(fs(presence), fs(absence))

                Log.objects.create(
                    field=hierarchy['cell'].profile.name + '\'s cell',
                    new_value=gs(data['presence'], data['absence']),
                    old_value=gs(old_presence, old_absence),
                    cell=hierarchy['cell'],
                    profile=request.user.profile,
                )

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)