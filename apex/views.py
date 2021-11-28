from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *
from .permissions import *

from .quota import compute_quota


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


class TeamView(APIView):

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


class ProjectsView(APIView):

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


class BoardView(APIView):

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

        profiles_id = [profile.id for profile in team.profiles.all()]

        for profile_id in profiles_id:
            Quota.objects.get_or_create(year=year, profile_id=profile_id)

        quotas = Quota.objects.filter(year=year, profile__in=profiles_id)

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)

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
                year=data['year'],
            )

            setattr(quota, data['element_type'], data['value'])
            quota.save()

            return Response(status=status.HTTP_200_OK)

        elif data['action'] == 'update_config':
            config = LeaveConfig.objects.get(app=hierarchy['app'])

            for key, val in data['value'].items():
                if key not in ['id', 'app']:
                    setattr(config, key, val)

            config.save()

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
        config = LeaveConfigSerializer(config).data

        quota, q = Quota.objects.get_or_create(
            year=year, profile_id=profile_id)

        base_quota = QuotaSerializer(quota).data

        cells = Cell.objects.filter(
            date__year=year, profile=profile_id)
        cells = CellSerializer(cells, many=True).data

        holidays = Holiday.objects.filter(date__year=year)
        holidays = HolidaySerializer(holidays, many=True).data

        computed_quota, detail_quota = compute_quota(
            cells=cells,
            quota=base_quota,
            config=config,
            holidays=holidays,
            detailed=True
        )

        result = {
            'team': TeamSerializer(team).data,
            'app': AppSerializer(app).data,
            'profile': ProfileSerializer(profile).data,
            'base_quota': base_quota,
            'computed_quota': computed_quota,
            'detail_quota': detail_quota,
            'config': config,
        }

        return Response(result)


class QuotaLightView(APIView):

    def get(self, request):
        end = request.query_params['end']
        app_id = request.query_params['app_id']
        profile_id = request.query_params['profile_id']
        month = request.query_params['month']
        year = request.query_params['year']

        config, c = LeaveConfig.objects.get_or_create(app_id=app_id)
        holidays = Holiday.objects.filter(date__year=year)
        quota, q = Quota.objects.get_or_create(
            year=year, profile_id=profile_id)

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

        quota, detail_quota = compute_quota(
            cells=CellSerializer(end_quota_cells, many=True).data,
            quota=QuotaSerializer(quota).data,
            config=LeaveConfigSerializer(config).data,
            holidays=HolidaySerializer(holidays, many=True).data,
            detailed=False
        )

        result = {
            'quota': quota,
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


class WorksView(APIView, WorksHelpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        config, c = RadiumConfig.objects.get_or_create(app_id=app_id)
        
        works = Work.objects.filter(
            date__month=month, date__year=year, apps__in=[app.id])

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app,context={'radium_config': True}).data,
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

        if data['action'] == 'create_work':
            work = Work.objects.create(
                color='light-blue',
                date=data['date'],
            )

            works_in_month = hierarchy['app'].work_set.filter(
                date=data['date'])
            position = len(works_in_month)

            link = AppWorkLink.objects.create(
                app=hierarchy['app'],
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
                        old_value=getattr(hierarchy['element'], key),
                        new_value=val,
                        profile=request.user.profile,
                        work=hierarchy['element']
                    )

                setattr(hierarchy['element'], key, val)
                hierarchy['element'].save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_work':
            work = hierarchy['element']
            app = hierarchy['app']

            for child_type in ['shift', 'limit', 's460']:
                child_set = getattr(work, child_type + '_set')

                for item in child_set.all():
                    if child_type == 'shift':
                        for part in item.part_set.all():
                            part.delete()

                    item.delete()

            for file in work.files.all():
                file.delete()
                # TODO file related suff

            work.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_work_position':
            for update in data['position_updates']:
                work_link = AppWorkLink.objects.get(
                    app=hierarchy['app'],
                    work_id=update['element_id']
                )

                work_link.position = update['element_position']
                work_link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_child':
            _type = data['element_type']
            child_model = globals()[_type.capitalize()]
            child_serializer = globals()[_type.capitalize() + 'Serializer']
            child_set = getattr(hierarchy['parent'], _type + '_set')

            position = len(child_set.all())

            child = child_model.objects.create(
                position=position,
                work=hierarchy['parent'],
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

            hierarchy['element'].delete()

            work = hierarchy['parent']
            child_set = getattr(work, _type + '_set')
            children = child_set.all().order_by('position')

            for i, child in enumerate(children):
                child.position = i
                child.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_child':
            del data['value']['id']
            del data['value']['work']

            for key, val in data['value'].items():
                setattr(hierarchy['element'], key, val)

            hierarchy['element'].save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_child_position':
            updates = data['position_updates']

            for update in updates:
                child_model = globals()[update['element_type'].capitalize()]
                child = child_model.objects.get(pk=update['element_id'])
                child.position = update['element_position']

                child.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_config':
            columns = data['value']

            config = RadiumConfig.objects.get(pk=data['element_id'])

            for column in columns:
                name = column['name']
                del column['name']

                for key, val in column.items():
                    setattr(config, name + '_' + key, val)

            config.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_parts':
            parts = list()

            for team_id in data['value']:
                part = Part.objects.create(
                    date=hierarchy['element'].date,
                    team=hierarchy['team'],
                    shift=hierarchy['element'],
                    work=hierarchy['parent'],
                )

                part_serialized = PartSerializer(part, context={
                    'parts': 'detail',
                    'profiles': 'detail',
                    'project': 'detail',
                }).data

                parts.append(part_serialized)

                day, c = Day.objects.get_or_create(
                    team=hierarchy['team'], date=hierarchy['element'].date)

                day.has_content = True
                day.save()

            return Response({'parts': parts})


        elif data['action'] == 'update_part':
            part = hierarchy['element']

            part.needs = data['value']['needs']
            part.locked = data['value']['locked']

            part.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_part':
            no_child = True
            date = hierarchy['element'].date

            hierarchy['element'].delete()

            day = Day.objects.get(team=hierarchy['team'], date=date)

            for child_type in ['task', 'note', 'file']:
                child_set = getattr(day, child_type + 's')

                if len(child_set.all()) > 0:
                    no_child = False
                    break

            if no_child:
                parts = Part.objects.filter(team=hierarchy['team'], date=date)

                if len(parts) > 0:
                    no_child = False

            if no_child:
                day.has_content = False
                day.save()

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


class ElementView(APIView, ElementHelpers):

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

                        result = {
                            'day': day_serialized,
                        }

                        return Response(result)


                return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_400_BAD_REQUEST)