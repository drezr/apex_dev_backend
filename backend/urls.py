from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from apex.views import *

urlpatterns = [
    path('admin', admin.site.urls),
    path('api-token-auth', obtain_auth_token),

    path('profile', ProfileView.as_view()),
    path('all_profiles', AllProfilesView.as_view()),
    path('home', HomeView.as_view()),
    path('myapex', MyApexView.as_view()),
    path('team', TeamView.as_view()),
    path('myapexdraft', MyApexDraftView.as_view()),
    path('contacts', ContactsView.as_view()),
    path('draft', DraftView.as_view()),
    path('templates', TemplatesView.as_view()),
    path('project', ProjectView.as_view()),
    path('templates', TemplatesView.as_view()),
    path('calendar', CalendarView.as_view()),
    path('planner', PlannerView.as_view()),
    path('calls', CallsView.as_view()),
    path('leaves', LeaveView.as_view()),
    path('quota', QuotaView.as_view()),
    path('quota_simple', QuotaSimpleView.as_view()),
    path('works', WorksView.as_view()),
    
    path('shifts', ShiftsView.as_view()),
    path('day', DayView.as_view()),
    path('cell', CellView.as_view()),
    path('presences', PresencesView.as_view()),
    path('apps', AppsView.as_view()),
    path('logs', LogsView.as_view()),
    path('messages', MessagesView.as_view()),
]
