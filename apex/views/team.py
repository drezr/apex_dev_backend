import uuid

from django.db.models import Q
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *

from ..misc.email_content import *


class TeamView(APIView, GenericHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']

        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'link': 'detail',
                'profiles': 'detail',
                'apps': 'detail',
                'message_count': True,
            }).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        profile_attrs = [
            'name',
            'phone',
            'ident',
            'grade',
            'field',
            'can_see_calendars'
        ]

        link_attrs = [
            'is_manager',
            'planner_is_editor',
            'planner_is_user',
            'draft_is_editor',
            'draft_is_user',
            'draft_can_see_private',
            'radium_is_editor',
            'watcher_is_user',
            'watcher_is_editor',
            'watcher_is_visible',
            'watcher_is_printable',
            'watcher_can_see_cells',
            'watcher_can_see_quotas',
            'watcher_color',
        ]


        if data['action'] == 'create_user':
            p = data['value']
            new_password = uuid.uuid4().hex[:8]
            username = p['username'].lower()

            user = User(
                username=username,
                password=new_password,
            )
            user.save()

            p_args = {pa: p[pa] for pa in profile_attrs}
            l_args = {la: p['link'][la] for la in link_attrs}

            profile = Profile.objects.create(user=user, **p_args)

            position = len(hierarchy['team'].profiles.all())

            team_profile_link = TeamProfileLink.objects.create(
                profile=profile,
                team=hierarchy['team'],
                position=position,
                **l_args,
            )

            profile_serialized = ProfileSerializer(profile).data
            profile_serialized['link'] = TeamProfileLinkSerializer(
                team_profile_link).data

            if p['send_password']:
                title = email_send_password_title[p['lang']]
                content = email_send_password_content[p['lang']] \
                            .replace('###name###', p['name']) \
                            .replace('###login###', username) \
                            .replace('###new_password###', new_password)

                send_mail(
                    title,
                    content,
                    'service@apex.wf',
                    [username],
                    fail_silently=False
                )


            return Response({'profile': profile_serialized})


        elif data['action'] == 'delete_user':
            if self.request.user.is_staff:
                profile = Profile.objects.get(pk=data['profile_id'])
                
                profile.user.delete()
                profile.delete()

                return Response(status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        elif data['action'] == 'add_links':
            profiles = list()
            tplinks = TeamProfileLink.objects.filter(
                team=hierarchy['team'])
            position = len(tplinks)

            for profile_id in data['value']:
                profile = Profile.objects.get(pk=profile_id)
                tplink = TeamProfileLink.objects.create(
                    profile=profile,
                    team=hierarchy['team'],
                    position=position,
                    watcher_color='blue',
                )

                profile_serialized = ProfileSerializer(profile).data
                profile_serialized['link'] = TeamProfileLinkSerializer(
                    tplink).data

                profiles.append(profile_serialized)

                position += 1



            return Response({'profiles': profiles})


        elif data['action'] == 'delete_link':
            tplink = TeamProfileLink.objects.get(
                profile_id=data['profile_id'],
                team=hierarchy['team'],
            )
            
            tplink.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_user':
            p = data['value']
            profile = Profile.objects.get(pk=data['value']['id'])
            tplink = TeamProfileLink.objects.get(
                profile=profile, team=hierarchy['team'])

            for attr in profile_attrs:
                setattr(profile, attr, p[attr])

            for attr in link_attrs:
                setattr(tplink, attr, p['link'][attr])

            profile.save()
            tplink.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_position':
            for p in data['value']:
                tplink = TeamProfileLink.objects.get(
                    profile_id=p['id'],
                    team=hierarchy['team'],
                )

                tplink.position = p['link']['position']
                tplink.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'check_email_exist':
            user = User.objects.filter(username=data['value'])

            return Response({'result': len(user) > 0})


        elif data['action'] == 'check_profiles_exist':
            profiles = Profile.objects.filter(name__icontains=data['value'])

            profile_list = list()

            for profile in profiles:
                p = ProfileSerializer(profile).data
                tplinks = TeamProfileLink.objects.filter(profile=profile)

                p['teams'] = list()

                for tplink in tplinks:
                    p['teams'].append(tplink.team.name)

                profile_list.append(p)


            return Response({
                'profiles': profile_list,
            })


        return Response(status=status.HTTP_400_BAD_REQUEST)