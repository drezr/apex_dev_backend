from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import *


class CircleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Circle
        fields = ['id', 'name']