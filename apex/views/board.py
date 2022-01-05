from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


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