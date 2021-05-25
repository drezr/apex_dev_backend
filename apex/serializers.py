from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import *


def check_context(context, arg, value):
    if context and arg in context and context[arg] == value:
        return True

    return False


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class CircleSerializer(serializers.ModelSerializer):

    teams = serializers.SerializerMethodField()

    class Meta:
        model = Circle
        fields = '__all__'

    def get_teams(self, circle):
        if check_context(self.context, 'teams', 'detail'):
            return TeamSerializer(
                circle.team_set.all(), many=True, context=self.context).data

        elif check_context(self.context, 'teams', 'id'):
            return [team.id for team in circle.team_set.all()]


class TeamSerializer(serializers.ModelSerializer):

    profiles = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'

    def get_profiles(self, team):
        if check_context(self.context, 'profiles', 'detail'):
            return ProfileSerializer(
                team.profiles.all(), many=True, context=self.context).data

        return [team.id for team in team.profiles.all()]


class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = App
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_tasks(self, project):
        if check_context(self.context, 'tasks', 'detail'):
            return TaskSerializer(
                project.tasks.all(), many=True, context=self.context).data

        elif check_context(self.context, 'tasks', 'id'):
            return [task.id for task in project.tasks.all()]


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
