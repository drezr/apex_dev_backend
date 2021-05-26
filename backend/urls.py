from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from apex.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token),
    path(r'api/', include('rest_framework.urls')),

    path('home/', HomeView.as_view()),
    path('team/<int:team_id>/', TeamView.as_view()),
    path('team/<int:team_id>/draft/<int:app_id>/', DraftView.as_view()),
    path('team/<int:team_id>/draft/<int:app_id>/templates/', TemplateView.as_view()),
    path('team/<int:team_id>/draft/<int:app_id>/project/<int:project_id>/', ProjectView.as_view()),
    path('team/<int:team_id>/watcher/<int:app_id>/calendar/<int:month>/<int:year>/', CalendarView.as_view()),
    path('team/<int:team_id>/radium/<int:app_id>/works/<int:month>/<int:year>/', WorksView.as_view()),
    
    path('shift/<int:shift_id>/', ShiftView.as_view()),
]
