from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *

from ..default_configs.leave_configs import leave_configs


class LeaveView(APIView, LeaveHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

        profiles_id = [profile.id for profile in team.profiles.all()]

        for profile_id in profiles_id:
            for leave_type in config.leave_type_set.all():
                Quota.objects.get_or_create(
                    code=leave_type.code,
                    year=year,
                    profile_id=profile_id,
                )

        quotas = Quota.objects.filter(
            profile__in=profiles_id, year=year)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'quotas': QuotaSerializer(quotas, many=True).data,
            'config': LeaveConfigSerializer(config).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if data['action'] == 'update_leave':
            quota = Quota.objects.get(
                profile=hierarchy['profile'],
                code=data['element_type'],
                year=data['year'],
            )

            quota.value = data['value']

            quota.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_leave_type':
            config = LeaveConfig.objects.get(app=hierarchy['app'])

            leave_types = config.leave_type_set.all()

            new_leave_type = LeaveType.objects.create(
                code=data['value']['code'],
                color=data['value']['color'],
                desc=data['value']['desc'],
                kind=data['value']['kind'],
                visible=data['value']['visible'],
                position=len(leave_types),
                config=config,
            )

            new_quotas = list()

            for profile in hierarchy['team'].profiles.all():
                new_quota = Quota.objects.create(
                    code=new_leave_type.code,
                    year=data['year'],
                    profile=profile,
                )

                new_quotas.append(new_quota)


            result = {
                'new_leave_type': LeaveTypeSerializer(
                    new_leave_type).data,
                'new_quotas': QuotaSerializer(
                    new_quotas, many=True).data,
            }

            return Response(result)


        elif data['action'] == 'update_leave_type':
            config = LeaveConfig.objects.get(app=hierarchy['app'])
            leave_type = LeaveType.objects.get(pk=data['value']['id'])

            for key, val in data['value'].items():
                if key in ['code', 'desc', 'kind', 'color', 'visible']:
                    if key == 'code' and leave_type.code != val:
                        for profile in hierarchy['team'].profiles.all():
                            quotas = Quota.objects.filter(
                                code=leave_type.code,
                                profile=profile,
                            )

                            for quota in quotas:
                                quota.code = val
                                quota.save()

                    setattr(leave_type, key, val)

            leave_type.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_leave_types_position':
            for lt in data['value']:
                leave_type = LeaveType.objects.get(pk=lt['id'])
                leave_type.position = lt['position']
                leave_type.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_leave_type':
            leave_type = LeaveType.objects.get(pk=data['value']['id'])
            leave_type.delete()

            for profile in hierarchy['team'].profiles.all():
                quotas = Quota.objects.filter(
                    code=data['value']['code'],
                    profile=profile,
                )

                for quota in quotas:
                    quota.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'add_leave_config':
            team = hierarchy['team']
            app = hierarchy['app']
            year = data['year']

            config = LeaveConfig.objects.get(app=app)

            for leave_type in config.leave_type_set.all():
                leave_type.delete()

            new_config = leave_configs[data['value']]

            for leave_type in new_config:
                LeaveType.objects.create(config=config, **leave_type)

            profiles_id = [profile.id for profile in team.profiles.all()]

            for profile_id in profiles_id:
                for leave_type in config.leave_type_set.all():
                    Quota.objects.get_or_create(
                        code=leave_type.code,
                        year=year,
                        profile_id=profile_id,
                    )

            quotas = Quota.objects.filter(
                profile__in=profiles_id, year=year)

            result = {
                'quotas': QuotaSerializer(quotas, many=True).data,
                'config': LeaveConfigSerializer(config).data,
            }

            return Response(result)


        elif data['action'] == 'create_quotas':
            config, c = LeaveConfig.objects.get_or_create(
                app=hierarchy['app'])

            for profile in hierarchy['team'].profiles.all():
                for leave_type in config.leave_type_set.all():
                    if leave_type.visible:
                        Quota.objects.get_or_create(
                            code=leave_type.code,
                            year=data['year'],
                            profile=profile,
                        )

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)