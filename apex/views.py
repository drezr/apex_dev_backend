from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *


class HomeView(APIView):

    def get(self, request):
        circles = Circle.objects.all()
        profile = request.user.profile

        user_teams = list()

        for circle in circles:
            teams = circle.team_set.filter(profiles__in=[profile])
            [user_teams.append(team) for team in teams]

        result = {
            'circles': CircleSerializer(
                circles, many=True,
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


class TemplateView(APIView):

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
                'templates': 'detail',
                'inputs': 'detail',
            }).data,
        }

        return Response(result)


class ProjectView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        project_id = request.query_params['project_id']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)
        project = Project.objects.get(pk=project_id)

        result = {
            'team': TeamSerializer(team).data,
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

        return Response(result)


class CalendarView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        profiles_id = [profile.id for profile in team.profiles.all()]
        
        days = Day.objects.filter(
            date__month=month, date__year=year, app=app.id)
        cells = Cell.objects.filter(
            date__month=month, date__year=year, profile__in=profiles_id)
        rrs = RR.objects.filter(date__month=month, date__year=year)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'days': DaySerializer(days, many=True).data,
            'cells': CellSerializer(cells, many=True).data,
            'rrs': RRSerializer(rrs, many=True).data,
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
        
        days = Day.objects.filter(
            date__month=month, date__year=year, app=app.id)

        days = DaySerializer(days, many=True, context={
            'link': 'detail',
            'tasks': 'detail',
            'subtasks': 'detail',
            'inputs': 'detail',
            'notes': 'detail',
            'files': 'detail',
        }).data

        for day in days:
            day['parts'] = list()

            parts = Part.objects.filter(team=team.id, date=day['date'])

            day['parts'] = PartSerializer(parts, many=True, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data

        result = {
            'team': TeamSerializer(team).data,
            'app': AppSerializer(app, context={
                'link': 'detail',
                'tasks': 'detail',
                'subtasks': 'detail',
                'inputs': 'detail',
                'notes': 'detail',
                'files': 'detail',
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
            Leave.objects.get_or_create(year=year, profile_id=profile_id)

        leaves = Leave.objects.filter(year=year, profile__in=profiles_id)

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'leaves': LeaveSerializer(leaves, many=True).data
        }

        return Response(result)


class DayView(APIView):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        date = request.query_params['date']

        day = Day.objects.get(app=app_id, date=date)

        day = DaySerializer(day, context={
            'link': 'detail',
            'tasks': 'detail',
            'notes': 'detail',
            'files': 'detail',
        }).data

        parts = Part.objects.filter(team=team_id, date=date)

        day['parts'] = PartSerializer(parts, many=True, context={
            'link': 'detail',
            'profiles': 'detail',
        }).data

        return Response({'day': day})


class CellView(APIView):

    def get(self, request):
        profile_id = request.query_params['profile_id']
        date = request.query_params['date']

        cell = Cell.objects.get(profile=profile_id, date=date)

        cell = CellSerializer(cell, context={
            'link': 'detail',
            'tasks': 'detail',
            'notes': 'detail',
            'files': 'detail',
            'calls': 'detail',
        }).data

        parts = Part.objects.filter(profiles__in=[profile_id], date=date)
        parts = PartSerializer(parts, many=True, context={
            'link': 'detail',
            'profiles': 'detail',
        }).data

        cell['parts'] = list()

        for part in parts:
            for profile in part['profiles']:
                if profile['link']['is_participant']:
                    if profile['id'] == profile_id:
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
        
        works = Work.objects.filter(
            date__month=month, date__year=year, apps__in=[app.id])

        result = {
            'team': TeamSerializer(team).data,
            'app': AppSerializer(app,context={'radium_config': True}).data,
            'works': WorkSerializer(works, many=True, context={
                'link': 'detail',
                'parent_id': app.id,
                'parent_type': 'app',
                'limits': 'detail',
                's460s': 'detail',
                'files': 'detail',
                'shifts': 'detail',
            }).data,
        }

        return Response(result)


class ShiftView(APIView):

    def get(self, request):
        shift_id = request.query_params['shift_id']

        shift = Shift.objects.get(pk=shift_id)

        result = {
            'shifts': ShiftSerializer(shift, context={
                'link': 'detail',
                'parts': 'detail',
                'profiles': 'detail',
            }).data,
        }

        return Response(result)