import uuid

from django.http import JsonResponse
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *
from .permissions import *

from .quota import compute_quota

from .radium_default_config import radium_default_config


class Helpers:

    def day_has_child(self, team, day):
        has_child = False

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(day, child_type + 's')

            if len(child_set.all()) > 0:
                has_child = True
                break

        if not has_child:
            parts = Part.objects.filter(team=team, date=day.date)

            if len(parts) > 0:
                has_child = True

        return has_child


    def cell_has_child(self, profile, cell):
        has_child = False

        parts = Part.objects.filter(
            profiles__in=[profile.id],
            date=cell.date,
        )

        for part in parts:
            for _profile in part.profiles.all():
                if _profile == profile:
                    _link = PartProfileLink.objects.get(
                        part=part,
                        profile=profile,
                    )

                    if _link.is_participant:
                        has_child = True
                        break

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(cell, child_type + 's')

            if len(child_set.all()) > 0:
                has_child = True
                break

        return has_child


    def cell_child_count(self, profile, cell):
        count = 0

        parts = Part.objects.filter(
            profiles__in=[profile.id],
            date=cell.date,
        )

        for part in parts:
            for _profile in part.profiles.all():
                if _profile == profile:
                    _link = PartProfileLink.objects.get(
                        part=part,
                        profile=profile,
                    )

                    if _link.is_participant:
                        count +=1

        for child_type in ['task', 'note', 'file']:
            child_set = getattr(cell, child_type + 's')
            child_set_count = len(child_set.all())

            if child_set_count > 0:
                count += child_set_count

        return count


    def set_day_cells_has_content(self, team, profiles, date):
        day, d = Day.objects.get_or_create(team=team, date=date)
        has_child = self.day_has_child(team, day)

        day.has_content = has_child
        day.save()

        for profile in profiles:
            cell, c = Cell.objects.get_or_create(
                profile=profile, date=date)

            has_child = self.cell_has_child(
                cell.profile, cell)

            cell.has_content = has_child
            cell.save()


class HomeView(APIView):

    def get(self, request):
        circles = Circle.objects.all()
        profile = request.user.profile

        user_teams = list()
        user_circles = list()

        for circle in circles:
            teams = circle.team_set.filter(profiles__in=[profile])
            [user_teams.append(team) for team in teams]

            for team in user_teams:
                if len(circle.team_set.filter(pk=team.id)):
                    user_circles.append(circle)


        result = {
            'circles': CircleSerializer(
                user_circles, many=True,
                context={'teams': 'detail'}
            ).data,
            'user_teams': TeamSerializer(user_teams, many=True).data,
        }


        return Response(result)


class ProfileView(APIView):

    def get(self, request):
        username = request.query_params['username']
        user = User.objects.get(username=username)

        result = {
            'profile': ProfileSerializer(user.profile, context={
                'user': 'detail'
            }).data,
        }

        return Response(result)


class AllProfilesView(APIView):

    def get(self, request):
        profiles = Profile.objects.all()

        all_profiles = [{'id': p.id, 'name': p.name} for p in profiles]
        result = {'all_profiles': all_profiles}

        return JsonResponse(result, safe=False)


class MyApexView(APIView):

    def get(self, request):
        result = {
            'profile': ProfileSerializer(request.user.profile, context={
                'apps': 'detail',
            }).data,
        }

        return Response(result)


class TeamView(APIView, GenericHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']

        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'link': 'detail',
                'profiles': 'detail',
                'apps': 'detail',
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

            user = User(
                username=p['username'].lower(),
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
                pass


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
            words = data['value'].split(' ')

            word1 = ''
            word2 = ''

            if len(words) >= 1:
                word1 = words[0].lower()

            if len(words) >= 2:
                word2 = words[1]

            profiles = Profile.objects.filter(
                Q(name__iexact='{0} {1}'.format(word1, word2)) |
                Q(name__iexact='{0} {1}'.format(word2, word1))
            )

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


class ProjectsView(APIView, GenericHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']

        result = {
            'team': TeamSerializer(Team.objects.get(pk=team_id), context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(App.objects.get(pk=app_id), context={
                'link': 'detail',
                'projects': 'detail',
            }).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'create_project':
            project = Project.objects.create(
                name=data['value']['name'],
                date=data['value']['date'],
                private=data['value']['private'],
            )

            position = len(hierarchy['app'].project_set.all())

            app_project_link = AppProjectLink.objects.create(
                app=hierarchy['app'],
                project=project,
                position=position,
            )

            project_serialized = ProjectSerializer(project).data
            project_serialized['link'] = AppProjectLinkSerializer(
                app_project_link).data

            return Response({'project': project_serialized})


        elif data['action'] == 'update_project':
            project = Project.objects.get(pk=data['element_id'])

            for arg in ['name', 'date', 'private', 'archived']:
                setattr(project, arg, data['value'][arg])

            project.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_project':
            project = Project.objects.get(pk=data['element_id'])

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)


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


class TemplatesView(APIView):

    def get(self, request):
        app_id = request.query_params['app_id']

        result = {
            'app': AppSerializer(App.objects.get(pk=app_id), context={
                'link': 'detail',
                'templates': 'detail',
                'inputs': 'detail',
            }).data,
        }

        return Response(result)


class ProjectView(APIView):

    def get(self, request):
        app_id = request.query_params['app_id']
        project_id = request.query_params['project_id']
        
        app = App.objects.get(pk=app_id)
        project = Project.objects.get(pk=project_id)

        result = {
            'app': AppSerializer(app).data,
            'project': ProjectSerializer(project, context={
                'link': 'detail',
                'tasks': 'detail',
                'subtasks': 'detail',
                'notes': 'detail',
                'files': 'detail',
                'inputs': 'detail',
            }).data,
        }

        if 'team_id' in request.query_params:
            team_id = request.query_params['team_id']
            team = Team.objects.get(pk=team_id)

            result['team'] = TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data

        return Response(result)


class CalendarView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        try:
            user_access = TeamProfileLink.objects.get(
                team_id=team_id,
                profile=request.user.profile,
            )
        except TeamProfileLink.DoesNotExist:
            user_access = None

        if user_access:
            if user_access.watcher_can_see_cells:
                profiles_id = [profile.id for profile in team.profiles.all()]

            else:
                profiles_id = [request.user.profile.id]

        else:
            profiles_id = []

        days = Day.objects.filter(
            date__month=month, date__year=year, team=team)
        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile__in=profiles_id)
        holidays = Holiday.objects.filter(date__month=month, date__year=year)

        leave_config, lc = LeaveConfig.objects.get_or_create(app_id=app_id)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'days': DaySerializer(days, many=True).data,
            'cells': CellSerializer(cells, many=True).data,
            'holidays': HolidaySerializer(holidays, many=True).data,
            'leave_config': LeaveConfigSerializer(leave_config).data,
        }

        return Response(result)


class BoardView(APIView, Helpers, BoardHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)
        
        days = Day.objects.filter(
            date__month=month, date__year=year, team=team)

        days = DaySerializer(days, many=True, context={
            'link': 'detail',
            'tasks': 'detail',
            'subtasks': 'detail',
            'inputs': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'teammates': 'detail',
        }).data

        for day in days:
            day['parts'] = list()

            parts = Part.objects.filter(team=team.id, date=day['date'])

            day['parts'] = PartSerializer(parts, many=True, context={
                'link': 'detail',
                'profiles': 'detail',
                'teammates': 'detail',
            }).data


        if len(app.folders.all()) == 0:
            new_folder = Folder.objects.create(
                name='1',
                color='light-blue',
            )

            AppFolderLink.objects.create(
                folder=new_folder,
                app=app,
                position=0,
            )


        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app, context={
                'link': 'detail',
                'folders': 'detail',
                'tasks': 'detail',
                'subtasks': 'detail',
                'inputs': 'detail',
                'notes': 'detail',
                'files': 'detail',
                'teammates': 'detail',
            }).data,
            'days': days,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        link_kwargs = dict()
        is_participant = data['value']

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'update_element_teammates':
            cell, c = Cell.objects.get_or_create(
                profile=hierarchy['profile'],
                date=hierarchy['parent'].date,
            )

            link_kwargs['cell'] = cell
            link_kwargs[data['element_type']] = hierarchy['element']
            link, l = hierarchy['link_model'].objects.get_or_create(
                **link_kwargs)

            if is_participant:
                child_count = self.cell_child_count(
                    hierarchy['profile'], cell)

                link.position = child_count - 1
                link.is_original = False
                link.save()

                cell.has_content = True
                cell.save()

            else:
                link.delete()

                cell.has_content = self.cell_has_child(
                    hierarchy['profile'], cell)
                cell.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_part_teammates':
            cell, c = Cell.objects.get_or_create(
                profile=hierarchy['profile'],
                date=hierarchy['parent'].date,
            )

            link, l = PartProfileLink.objects.get_or_create(
                profile=hierarchy['profile'],
                part=hierarchy['parent'],
            )

            link.is_participant = is_participant
            link.save()

            cell.has_content = self.cell_has_child(
                hierarchy['profile'], cell)
            cell.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'add_folder':
            app_folders = hierarchy['app'].folders.all()
            position = len(app_folders)

            folder = Folder.objects.create(
                name=position + 1, color='blue')

            app_folder_link = AppFolderLink.objects.create(
                app=hierarchy['app'],
                folder=folder,
                position=position,
            )

            folder_serialized = FolderSerializer(folder, context={
                'tasks': 'detail',
                'subtasks': 'detail',
                'inputs': 'detail',
                'notes': 'detail',
                'files': 'detail',
                'teammates': 'detail',
            }).data
            
            folder_serialized['link'] = AppFolderLinkSerializer(
                app_folder_link).data

            return Response({'folder': folder_serialized})


        elif data['action'] == 'update_folders_position':
            for folder in data['value']:
                link = AppFolderLink.objects.get(
                    app=hierarchy['app'],
                    folder_id=folder['id'],
                )

                link.position = folder['link']['position']
                link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_folder':
            folder = Folder.objects.get(pk=data['value']['id'])

            folder.name = data['value']['name']
            folder.color = data['value']['color']

            folder.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_foler':
            folder = Folder.objects.get(pk=data['element_id'])

            for child_type in ['task', 'note', 'file']:
                child_set = getattr(folder, child_type + 's')

                if child_type == 'file':
                    # DO FILE STUFF
                    pass

                for child in child_set.all():
                    if child_type == 'task':
                        for grandchild_type in ['subtask', 'note', 'file', 'input']:
                            grandchild_set = getattr(
                                child, grandchild_type + 's')

                            for grandchild in grandchild_set.all():
                                if grandchild_type == 'file':
                                    # DO FILE STUFF
                                    pass

                                grandchild.delete()

                    child.delete()

            folder.delete()

            return Response(status=status.HTTP_200_OK)



        return Response(status=status.HTTP_400_BAD_REQUEST)


class CallsView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        profiles_id = [profile.id for profile in team.profiles.all()]

        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile__in=profiles_id)

        calls = list()

        for cell in cells:
            for call in cell.calls.all():
                call = CallSerializer(call, context={
                    'files': 'detail',
                    'links': 'detail',
                }).data

                call['date'] = cell.date
                call['profile'] = ProfileSerializer(cell.profile).data
                calls.append(call)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'calls': calls,
        }

        return Response(result)


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
                config=config,
                position=len(leave_types),
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


        return Response(status=status.HTTP_400_BAD_REQUEST)


class QuotaView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        profile_id = request.query_params['profile_id']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)
        profile = Profile.objects.get(pk=profile_id)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

        for leave_type in config.leave_type_set.all():
            if leave_type.visible:
                Quota.objects.get_or_create(
                    code=leave_type.code,
                    year=year,
                    profile_id=profile_id,
                )

        quotas = Quota.objects.filter(
            profile=profile_id, year=year)
        cells = Cell.objects.filter(
            date__year=year, profile=profile_id)
        holidays = Holiday.objects.filter(date__year=year)


        base_quotas, computed_quotas, detailed_quotas = compute_quota(
            cells=CellSerializer(cells, many=True).data,
            quotas=QuotaSerializer(quotas, many=True).data,
            config=LeaveConfigSerializer(config).data,
            holidays=HolidaySerializer(holidays, many=True).data,
            detailed=True
        )

        result = {
            'team': TeamSerializer(team).data,
            'app': AppSerializer(app).data,
            'config': LeaveConfigSerializer(config).data,
            'profile': ProfileSerializer(profile).data,
            'base_quotas': base_quotas,
            'computed_quotas': computed_quotas,
            'detailed_quotas': detailed_quotas,
        }

        return Response(result)


class QuotaLightView(APIView):

    def get(self, request):
        end = request.query_params['end']
        app_id = request.query_params['app_id']
        profile_id = request.query_params['profile_id']
        month = request.query_params['month']
        year = request.query_params['year']

        holidays = Holiday.objects.filter(date__year=year)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

        for leave_type in config.leave_type_set.all():
            if leave_type.visible:
                Quota.objects.get_or_create(
                    code=leave_type.code,
                    year=year,
                    profile_id=profile_id,
                )


        quotas = Quota.objects.filter(profile=profile_id, year=year)

        end_quota_cells = None

        if end == 'month_start':
            end_quota_cells = Cell.objects.filter(
                date__month__lt=month,
                date__year=year,
                profile=profile_id,
            )

        elif end == 'month_end':
            end_quota_cells = Cell.objects.filter(
                date__month__lte=month,
                date__year=year,
                profile=profile_id,
            )

        elif end == 'year_end':
            end_quota_cells = Cell.objects.filter(
                date__month__lte=12,
                date__year=year,
                profile=profile_id,
            )

        base_quotas, computed_quotas, detailed_quotas = compute_quota(
            cells=CellSerializer(end_quota_cells, many=True).data,
            quotas=QuotaSerializer(quotas, many=True).data,
            config=LeaveConfigSerializer(config).data,
            holidays=HolidaySerializer(holidays, many=True).data,
            detailed=False
        )

        result = {
            'quota': computed_quotas,
        }

        return Response(result)


class DayView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        date = request.query_params['date']

        day, c = Day.objects.get_or_create(team_id=team_id, date=date)

        day = DaySerializer(day, context={
            'link': 'detail',
            'tasks': 'detail',
            'subtasks': 'detail',
            'inputs': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'links': 'detail',
            'teammates': 'detail',
        }).data

        parts = Part.objects.filter(team=team_id, date=date)

        day['parts'] = PartSerializer(parts, many=True, context={
            'link': 'detail',
            'profiles': 'detail',
            'teammates': 'detail',
        }).data

        return Response({'day': day})


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
            hierarchy['cell'].presence = data['presence']
            hierarchy['cell'].absence = data['absence']
            hierarchy['cell'].color = data['color']

            hierarchy['cell'].save()

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)


class WorksView(APIView, WorksHelpers, Helpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        config, is_new = RadiumConfig.objects.get_or_create(app_id=app_id)

        if is_new:
            for column in radium_default_config:
                RadiumConfigColumn.objects.create(
                    name=column['name'],
                    position=column['position'],
                    width=column['width'],
                    textsize=column['textsize'],
                    visible=column['visible'],
                    config=config,
                )
        
        works = Work.objects.filter(
            date__month=month, date__year=year, apps__in=[app.id])

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'config': RadiumConfigSerializer(config).data,
            'works': WorkSerializer(works, many=True, context={
                'link': 'detail',
                'parent_id': app.id,
                'parent_type': 'app',
                'limits': 'detail',
                's460s': 'detail',
                'files': 'detail',
                'shifts': 'detail',
                'apps': 'id',
            }).data,
        }

        return Response(result)


    def post(self, request):
        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        team = hierarchy['team']
        app = hierarchy['app']
        source = hierarchy['source']
        parent = hierarchy['parent']
        element = hierarchy['element']

        if data['action'] == 'create_work':
            work = Work.objects.create(
                color='light-blue',
                date=data['date'],
            )

            works_in_month = app.work_set.filter(
                date=data['date'])
            position = len(works_in_month)

            link = AppWorkLink.objects.create(
                app=app,
                work=work,
                position=position,
                is_original=True,
            )

            work_serialized = WorkSerializer(work, context={
                'limits': 'detail',
                's460s': 'detail',
                'files': 'detail',
                'shifts': 'detail',
                'apps': 'id',
            }).data

            work_serialized['link'] = AppWorkLinkSerializer(link).data

            return Response({
                'work': work_serialized,
            })


        elif data['action'] == 'update_work':
            for key, val in data['value'].items():
                if 'color' not in key:
                    Log.objects.create(
                        field=key,
                        old_value=getattr(element, key),
                        new_value=val,
                        profile=request.user.profile,
                        work=element
                    )

                setattr(element, key, val)
                element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_work':
            for child_type in ['shift', 'limit', 's460']:
                child_set = getattr(element, child_type + '_set')

                for item in child_set.all():
                    if child_type == 'shift':
                        for part in item.part_set.all():
                            date = part.date
                            profiles = [p for p in part.profiles.all()]
                            part_team = part.team

                            part.delete()

                            self.set_day_cells_has_content(
                                part_team, profiles, date)


            for file in element.files.all():
                file.delete()
                # TODO file related suff

            element.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_work_position':
            for update in data['position_updates']:
                work_link = AppWorkLink.objects.get(
                    app=app,
                    work_id=update['element_id']
                )

                work_link.position = update['element_position']
                work_link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_child':
            _type = data['element_type']
            child_model = globals()[_type.capitalize()]
            child_serializer = globals()[
                _type.capitalize() + 'Serializer']
            child_set = getattr(parent, _type + '_set')

            position = len(child_set.all())

            child = child_model.objects.create(
                position=position,
                work=parent,
            )

            child_serialized = child_serializer(child, context={
                'parts': 'detail',
            }).data

            data = dict()
            data[_type] = child_serialized

            return Response(data)


        elif data['action'] == 'delete_child':
            _type = data['element_type']
            child_model = globals()[_type.capitalize()]

            date = element.date

            if element.type == 'shift':
                for part in element.part_set.all():
                    profiles = [p for p in part.profiles.all()]
                    part_team = part.team

                    part.delete()

                    self.set_day_cells_has_content(
                        part_team, profiles, date)


            element.delete()

            child_set = getattr(parent, _type + '_set')
            children = child_set.all().order_by('position')

            for i, child in enumerate(children):
                child.position = i
                child.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_child':
            del data['value']['id']
            del data['value']['work']

            for key, val in data['value'].items():
                setattr(element, key, val)

            if element.type == 'shift':
                for part in element.part_set.all():
                    old_date = part.date
                    part.date = element.date
                    part_team = part.team

                    part.save()

                    if old_date != element.date:
                        profiles = [p for p in part.profiles.all()]

                        self.set_day_cells_has_content(
                            part_team, profiles, old_date)

                        self.set_day_cells_has_content(
                            part_team, profiles, element.date)

            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_child_position':
            updates = data['position_updates']

            for update in updates:
                child_model = globals()[
                    update['element_type'].capitalize()]
                child = child_model.objects.get(
                    pk=update['element_id'])
                child.position = update['element_position']

                child.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_config':
            columns = data['value']

            config = RadiumConfig.objects.get(pk=data['element_id'])

            for column in columns:
                config_column = RadiumConfigColumn.objects.get(
                    pk=column['id'])

                for attr in ['id', 'name', 'config']:
                    del column[attr]

                for key, val in column.items():
                    setattr(config_column, key, val)

                config_column.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_parts':
            parts = list()

            for team_id in data['value']:
                part = Part.objects.create(
                    date=element.date,
                    team=team,
                    shift=element,
                    work=parent,
                )

                part_serialized = PartSerializer(part, context={
                    'parts': 'detail',
                    'profiles': 'detail',
                    'project': 'detail',
                }).data

                parts.append(part_serialized)

                day, c = Day.objects.get_or_create(
                    team=team, date=element.date)

                day.has_content = True
                day.save()

            return Response({'parts': parts})


        elif data['action'] == 'update_part':
            element.needs = data['value']['needs']
            element.locked = data['value']['locked']

            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_part':
            date = element.date
            profiles = [p for p in element.profiles.all()]
            part_team = element.team

            element.delete()

            self.set_day_cells_has_content(part_team, profiles, date)

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_part_profile_link':
            cell, c = Cell.objects.get_or_create(
                profile_id=data['profile_id'],
                date=element.date,
            )

            profile = Profile.objects.get(pk=data['profile_id'])

            link, c = PartProfileLink.objects.get_or_create(
                part=element,
                profile=profile,
            )

            profile_serialized = ProfileSerializer(profile).data
            profile_serialized['link'] = PartProfileLinkSerializer(
                link).data

            return Response({'profile': profile_serialized})


        elif data['action'] == 'update_part_profile_link':
            profile = Profile.objects.get(pk=data['profile_id'])

            link = PartProfileLink.objects.get(
                part=element,
                profile=profile,
            )

            is_participant = data['value']['is_participant'] \
                             and not link.is_participant

            is_not_participant = not data['value']['is_participant'] \
                                 and link.is_participant
            link.is_available = data['value']['is_available']
            link.is_participant = data['value']['is_participant']
            link.save()

            if is_participant:
                cell = Cell.objects.get(
                    profile_id=data['profile_id'],
                    date=element.date,
                )

                cell.has_content = True
                cell.save()

            if is_not_participant:
                cell = Cell.objects.get(
                    profile_id=data['profile_id'],
                    date=element.date,
                )

                has_child = self.cell_has_child(profile, cell)

                if not has_child:
                    cell.has_content = False
                    cell.save()

            return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShiftsView(APIView):

    def get(self, request):
        work_id = request.query_params['work_id']

        shifts = Shift.objects.filter(work=work_id)

        result = {
            'shifts': ShiftSerializer(shifts, context={
                'link': 'detail',
                'parts': 'detail',
                'profiles': 'detail',
                'project': 'detail',
            }, many=True).data,
        }

        return Response(result)


class PresencesView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        date = request.query_params['date']

        team = Team.objects.get(pk=team_id)
        presences = list()

        for profile in team.profiles.all():
            cell, c = Cell.objects.get_or_create(
                profile_id=profile.id, date=date)

            presences.append({
                'profile_id': profile.id,
                'presence': cell.presence,
                'absence': cell.absence,
            })

        result = {
            'presences': presences,
        }

        return Response(result)


class AppsView(APIView):

    def get(self, request):
        circles = Circle.objects.all()
        profile = request.user.profile

        user_teams = list()
        user_circles = list()

        for circle in circles:
            teams = circle.team_set.filter(profiles__in=[profile])
            [user_teams.append(team) for team in teams]

            for team in user_teams:
                if len(circle.team_set.filter(pk=team.id)):
                    user_circles.append(circle)


        result = {
            'circles': CircleSerializer(
                user_circles, many=True,
                context={'teams': 'detail', 'apps': 'detail'}
            ).data,
        }

        return Response(result)


class LogsView(APIView):

    def get(self, request):
        if 'cell_id' in request.query_params:
            cell_id = request.query_params['cell_id']
            logs = Log.objects.filter(cell=cell_id).order_by('-date')

        elif 'work_id' in request.query_params:
            work_id = request.query_params['work_id']
            field = request.query_params['field']
            logs = Log.objects.filter(
                work=work_id, field=field).order_by('-date')

        result = {
            'logs': LogSerializer(logs, many=True).data,
        }

        return Response(result)


class MessagesView(APIView):

    def get(self, request):
        if 'app_id' in request.query_params:
            app_id = request.query_params['app_id']
            messages = Message.objects.filter(app=app_id).order_by('-date')

        result = {
            'messages': MessageSerializer(messages, many=True).data,
        }

        return Response(result)


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


class ElementView(APIView, ElementHelpers, Helpers):

    def get_child_count(self, data, element, hierarchy, option='all'):
        count = 0

        if option == 'all' or option == 'exclude_calls':
            if data['parent_type'] != 'task':
                count += len(hierarchy[element].tasks.all())

            if data['parent_type'] == 'task':
                count += len(hierarchy[element].inputs.all())

            if data['parent_type'] in ['task', 'folder', 'day', 'cell']:
                count += len(hierarchy[element].notes.all())
                count += len(hierarchy[element].files.all())

        if option == 'all' or option == 'only_calls':
            if data['parent_type'] == 'cell':
                count += len(hierarchy[element].calls.all())


        if option == 'all' or option == 'exclude_calls':
            if data['parent_type'] == 'day':
                parts = Part.objects.filter(
                    team=hierarchy['team'], date=hierarchy['parent'].date)

                count += len(parts)

            elif data['parent_type'] == 'cell':
                pass

                #TODO PartProfileLink + Cell check


        return count


    def post(self, request):
        create_kwargs = dict()
        link_kwargs = dict()
        element_serialized = None

        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'create':
            if data['element_type'] in ['task', 'subtask']:
                create_kwargs = {'status': 'pending'}

            elif data['element_type'] == 'input':
                create_kwargs = {'kind': data['kind']}

            elif data['element_type'] == 'note':
                create_kwargs = {'profile': request.user.profile}

            element = hierarchy['element_model'].objects.create(
                **create_kwargs)
            element_serialized = hierarchy['element_serializer'](
                element, context={
                    'tasks': 'detail',
                    'subtasks': 'detail',
                    'inputs': 'detail',
                    'notes': 'detail',
                    'files': 'detail',
                    'calls': 'detail',
                    'links': 'detail',
                    'teammates': 'detail',
                }).data

            link_kwargs[data['parent_type']] = hierarchy['parent']
            link_kwargs[data['element_type']] = element
            link_kwargs['position'] = self.get_child_count(
                data, 'parent', hierarchy) + 1
            link_kwargs['is_original'] = True

            link = hierarchy['link_model'].objects.create(**link_kwargs)
            element_serialized['link'] = hierarchy['link_serializer'](
                link).data

            if data['parent_type'] in ['day', 'cell']:
                if data['element_type'] == 'call':
                    hierarchy['parent'].has_call = True

                else:
                    hierarchy['parent'].has_content = True

                hierarchy['parent'].save()

            result = {
                data['element_type']: element_serialized,
            }

            return Response(result)


        elif data['action'] == 'update':
            element = hierarchy['element']

            for field in ['name', 'key', 'value', 'heading', 'status',
                          'kind', 'start', 'end', 'description']:
                if data[field]:
                    setattr(element, field, data[field])

            if data['element_type'] == 'file':
                # TO DO: update file stuff
                pass

            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete':
            link_kwargs[data['parent_type']] = hierarchy['parent']
            link_kwargs[data['element_type']] = hierarchy['element']

            link = hierarchy['link_model'].objects.get(**link_kwargs)
            element = hierarchy['element']

            possible_children = {
                'task': ['note', 'file', 'input', 'subtask'],
                'call': ['file'],
            }

            if data['parent_type'] in ['day', 'cell']:
                if data['element_type'] == 'call':
                    count = self.get_child_count(
                        data, 'parent', hierarchy, 'only_calls')

                    if count <= 1:
                        hierarchy['parent'].has_call = False

                else:
                    count = self.get_child_count(
                        data, 'parent', hierarchy, 'exclude_calls')

                    if count <= 1:
                        hierarchy['parent'].has_content = False


                    cell_link_model = globals()[
                        'Cell' +
                        data['element_type'].capitalize() + 'Link']

                    cell_link_kwargs = dict()
                    cell_link_kwargs[data['element_type']] = hierarchy['element']

                    cell_links = cell_link_model.objects.filter(
                        **cell_link_kwargs
                    )

                    for cell_link in cell_links:
                        cell = cell_link.cell

                        child_count = self.cell_child_count(cell.profile, cell)

                        if child_count == 1:
                            cell.has_content = False
                            cell.save()

                
                hierarchy['parent'].save()

            if link.is_original:
                for element_type in possible_children:
                    if data['element_type'] == element_type:
                        for child_type in possible_children[element_type]:
                            child_set = getattr(element, child_type + 's')

                            for child in child_set.all():
                                child.delete()

                                if child_type == 'file':
                                    # TO DO: delete file stuff
                                    pass

                element.delete()

            else:
                link.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'position':
            element = hierarchy['element']

            for child_data in data['position_updates']:
                link_kwargs = dict()

                child_set = getattr(element, child_data['element_type'] + 's')
                child = child_set.get(pk=child_data['element_id'])

                link_model = globals()[
                    data['element_type'].capitalize() +
                    child_data['element_type'].capitalize() + 'Link']

                link_kwargs[child_data['element_type']] = child
                link_kwargs[data['element_type']] = hierarchy['element']

                link = link_model.objects.get(**link_kwargs)

                if link:
                    link.position = child_data['position']
                    link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'move':
            old_link_kwargs = dict()
            new_link_kwargs = dict()

            old_link_kwargs[data['parent_type']] = hierarchy['parent']
            old_link_kwargs[data['element_type']] = hierarchy['element']
            new_link_kwargs[data['new_parent_type']] = hierarchy['new_parent']
            new_link_kwargs[data['element_type']] = hierarchy['element']

            old_link = hierarchy['link_model'].objects.get(**old_link_kwargs)
            new_link, c = hierarchy['new_link_model'].objects.get_or_create(
                **new_link_kwargs)

            cell_link_model = globals()[
                'Cell' + data['element_type'].capitalize() + 'Link']

            cell_link_kwargs = dict()
            cell_link_kwargs[data['element_type']] = hierarchy['element']
            cell_links = cell_link_model.objects.filter(**cell_link_kwargs)

            if old_link and new_link:
                if old_link == new_link:
                    setattr(old_link, data['parent_type'],
                            hierarchy['new_parent'])
                    old_link.save()

                else:
                    old_link.delete()

                    setattr(new_link, data['new_parent_type'],
                            hierarchy['new_parent'])
                    new_link.save()

                    if data['parent_type'] == 'day':
                        parent_child_count = self.get_child_count(
                            data, 'parent', hierarchy, 'exclude_calls')

                        if parent_child_count == 0:
                            hierarchy['parent'].has_content = False
                            hierarchy['parent'].save()

                    if data['new_parent_type'] == 'day':
                        hierarchy['new_parent'].has_content = True
                        hierarchy['new_parent'].save()

                        day_serialized = DaySerializer(
                            hierarchy['new_parent'], context={
                                'link': 'detail',
                                'tasks': 'detail',
                                'subtasks': 'detail',
                                'inputs': 'detail',
                                'notes': 'detail',
                                'files': 'detail',
                                'links': 'detail',
                                'teammates': 'detail',
                            }).data

                        day_serialized['link'] = \
                            hierarchy['new_link_serializer'](new_link).data


                        for cell_link in cell_links:
                            old_cell = cell_link.cell
                            new_cell, c = Cell.objects.get_or_create(
                                profile=old_cell.profile,
                                date=hierarchy['new_parent'].date
                            )

                            new_cell.has_content = True
                            new_cell.save()

                            cell_link.cell = new_cell

                            child_count = self.cell_child_count(
                                new_cell.profile, new_cell)

                            cell_link.position = child_count

                            cell_link.save()

                            has_child = self.cell_has_child(
                                old_cell.profile, old_cell)

                            if not has_child:
                                old_cell.has_content = False
                                old_cell.save()


                        result = {
                            'day': day_serialized,
                        }

                        return Response(result)


                    if data['new_parent_type'] == 'folder':
                        for cell_link in cell_links:
                            cell = cell_link.cell
                            cell_link.delete()

                            child_count = self.cell_child_count(
                                cell.profile, cell)

                            if child_count == 0:
                                cell.has_content = False
                                cell.save()


                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)