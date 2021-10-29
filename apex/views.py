from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *

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


class DraftView(APIView):

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


class MyApexDraftView(APIView):

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
            date__month=month, date__year=year, app=app.id)
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


class PlannerView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        watcher_id = None

        for _app in team.app_set.all():
            if _app.app == 'watcher':
                watcher_id = _app.id
                break
        
        days = Day.objects.filter(
            date__month=month, date__year=year, app=watcher_id)

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


class LeaveView(APIView):

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


class QuotaSimpleView(APIView):

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

        day, c = Day.objects.get_or_create(app_id=app_id, date=date)

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


class CellView(APIView):

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


class WorksView(APIView):

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

        result = {
            'circles': CircleSerializer(
                circles, many=True,
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
                return Response(status=status.HTTP_500_INTERNAL_SERVER_EHolidayOR)


        result = {
            'app': app,
        }

        return Response(result)