from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class WorksMobileView(APIView):

    def get(self, request):
        profile_id = request.query_params['profile_id']
        month = request.query_params['month']
        year = request.query_params['year']

        profile = Profile.objects.get(pk=profile_id)
        tp_links = TeamProfileLink.objects.filter(profile=profile)
        teams = [tp_link.team for tp_link in tp_links.all()]

        parts = Part.objects.filter(
            team__in=teams, date__month=month, date__year=year)
        parts = PartSerializer(parts, many=True, context={
            'link': 'detail',
            'profiles': 'detail',
            'teammates': 'detail',
        }).data

        result = {
            'parts': parts,
        }

        return Response(result)