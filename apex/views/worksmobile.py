from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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


    def post(self, request):
        if request.data['action'] == 'create_part_profile_link':
            profile = Profile.objects.get(pk=request.data['profile_id'])

            link, c = PartProfileLink.objects.get_or_create(
                part_id=request.data['part_id'],
                profile=profile,
            )

            profile_serialized = ProfileSerializer(profile).data
            profile_serialized['link'] = PartProfileLinkSerializer(
                link).data

            return Response({'profile': profile_serialized})


        elif request.data['action'] == 'update_part_profile_link':
            link = PartProfileLink.objects.get(
                part_id=request.data['part_id'],
                profile_id=request.data['profile_id'],
            )

            link.is_available = request.data['is_available']

            link.save()

            return Response(status=status.HTTP_200_OK)