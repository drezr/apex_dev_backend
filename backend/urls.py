from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from apex.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token),
    path(r'api/', include('rest_framework.urls')),

    path('home/', Home.as_view()),
    path('hub/<int:team_id>/', Hub.as_view()),
    path('draft/<int:app_id>/', Draft.as_view()),
    path('project/<int:project_id>/', ProjectView.as_view()),
]
