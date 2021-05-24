from django.http import HttpResponse, JsonResponse

from .models import *
from .serializers import *


def home(request):
    if request.method == 'GET':
        circles = Circle.objects.all()
        serializer = CircleSerializer(circles, many=True)

        return JsonResponse(serializer.data, safe=False)

    return HttpResponse(status=403)