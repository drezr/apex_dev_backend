import shutil
import uuid

from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *

from ..default_configs.radium_default_config import radium_default_config


class WorksView(APIView, WorksHelpers, Helpers):

    def get(self, request):
        team_id = request.query_params['team_id']
        app_id = request.query_params['app_id']
        month = request.query_params['month']
        year = request.query_params['year']

        team = Team.objects.get(pk=team_id)
        app = App.objects.get(pk=app_id)

        config, is_new = RadiumConfig.objects.get_or_create(app_id=app_id)

        if is_new:
            for column in radium_default_config:
                RadiumConfigColumn.objects.create(
                    name=column['name'],
                    position=column['position'],
                    width=column['width'],
                    textsize=column['textsize'],
                    visible=column['visible'],
                    multiple=column['multiple'],
                    clickable=column['clickable'],
                    path=column['path'],
                    config=config,
                )
        
        works = Work.objects.filter(
            date__month=month, date__year=year, apps__in=[app.id])

        result = {
            'team': TeamSerializer(team, context={
                'link': 'detail',
                'profiles': 'detail',
            }).data,
            'app': AppSerializer(app).data,
            'config': RadiumConfigSerializer(config).data,
            'message_count': Message.objects.filter(app=app).count(),
            'works': WorkSerializer(works, many=True, context={
                'link': 'detail',
                'parent_id': app.id,
                'parent_type': 'app',
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

        team = hierarchy['team']
        app = hierarchy['app']
        source = hierarchy['source']
        parent = hierarchy['parent']
        element = hierarchy['element']

        if data['action'] == 'create_work':
            work = Work.objects.create(
                color='light-blue',
                date=data['date'],
            )

            works_in_month = app.work_set.filter(
                date=data['date'])
            position = len(works_in_month)

            link = AppWorkLink.objects.create(
                app=app,
                work=work,
                position=position,
                is_original=True,
            )

            work_serialized = WorkSerializer(work, context={
                'files': 'detail',
                'shifts': 'detail',
                'apps': 'id',
            }).data

            work_serialized['link'] = AppWorkLinkSerializer(link).data

            return Response({
                'work': work_serialized,
            })


        elif data['action'] == 'update_work':
            column_updates = data['value']['columns']
            logs = data['value']['logs']

            new_columns = list()

            for column_update in column_updates:
                if 'id' in column_update and column_update['id']:
                    column = element.columns.get(pk=column_update['id'])

                    column.value = column_update['value']
                    column.bg_color = column_update['bg_color']
                    column.text_color = column_update['text_color']

                    for row_update in column_update['rows']:
                        row = column.rows.get(pk=row_update['id'])

                        del row_update['id']
                        del row_update['created_date']
                        del row_update['updated_date']
                        del row_update['work_column']

                        for key, val in row_update.items():
                            setattr(row, key, val)

                        row.save()

                    column.save()

                else:
                    value = None if not 'value' in column_update \
                        else column_update['value']
                    bg_color = None if not 'bg_color' in column_update \
                        else column_update['bg_color']
                    text_color = None if not 'text_color' in column_update \
                        else column_update['text_color']

                    column = WorkColumn.objects.create(
                        name=column_update['name'],
                        value=value,
                        bg_color=bg_color,
                        text_color=text_color,
                        work=element,
                    )

                new_columns.append(WorkColumnSerializer(column).data)

            for log in logs:
                old_value = '' if not 'old_value' in log else log['old_value']
                Log.objects.create(
                    field=log['column_name'],
                    new_value=log['new_value'],
                    old_value=old_value,
                    work=element,
                    profile=request.user.profile,
                )

            if element.color != data['value']['color']:
                element.color = data['value']['color']
                element.save()

            return Response({'columns': new_columns})


        elif data['action'] == 'delete_work':
            link = AppWorkLink.objects.get(app=app, work=element)

            if link.is_original:
                for shift in element.shift_set.all():
                    for part in shift.part_set.all():
                        date = part.date
                        profiles = [p for p in part.profiles.all()]
                        part_team = part.team

                        part.delete()

                        self.set_day_cells_has_content(part_team, profiles, date)



                for column in element.columns.all():
                    column.delete()


                for file in element.files.all():
                    path = '{0}/{1}/'.format(default_storage.location, file.uid)
                    shutil.rmtree(path)
                    
                    file.delete()

                element.delete()


            else:
                link.delete()


            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_work_position':
            for update in data['position_updates']:
                work_link = AppWorkLink.objects.get(
                    app=app,
                    work_id=update['element_id']
                )

                work_link.position = update['element_position']
                work_link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_child':
            column, c = WorkColumn.objects.get_or_create(
                work=parent,
                name=data['element_type'],
            )
            column_serialized = WorkColumnSerializer(column).data

            if data['element_type'] == 'shifts':
                position = len(parent.shift_set.all())

                shift = Shift.objects.create(
                    position=position,
                    work=parent,
                )

                shift_serialized = ShiftSerializer(shift, context={
                    'parts': 'detail',
                }).data

                return Response({
                    'column': column_serialized,
                    'child': shift_serialized,
                })

            else:
                position = len(column.rows.all())

                row = WorkRow.objects.create(
                    position=position,
                    work_column=column,
                )

                row_serialized = WorkRowSerializer(row).data

                return Response({
                    'column': column_serialized,
                    'child': row_serialized,
                })


        elif data['action'] == 'delete_child':
            if data['element_type'] == 'shift':
                date = element.date

                for part in element.part_set.all():
                    profiles = [p for p in part.profiles.all()]
                    part_team = part.team  

                    part.delete()

                    self.set_day_cells_has_content(
                        part_team, profiles, date)

                element.delete()


            elif data['element_type'] == 'file':
                path = '{0}/{1}/'.format(default_storage.location, element.uid)
                shutil.rmtree(path)

                element.delete()


            else:
                column = parent.columns.get(name=data['value']['column_name'])
                row = column.rows.get(pk=data['element_id'])
                row.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_shift':
            element.date = data['value']['date']
            element.shift = data['value']['shift']

            element.save()

            for part in element.part_set.all():
                old_date = part.date
                part.date = element.date
                part_team = part.team

                part.save()

                if old_date != element.date:
                    profiles = [p for p in part.profiles.all()]

                    self.set_day_cells_has_content(
                        part_team, profiles, old_date)

                    self.set_day_cells_has_content(
                        part_team, profiles, element.date)

            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_child_position':
            updates = data['position_updates']

            for update in updates:
                child = None

                if update['column_name'] == 'shifts':
                    child = element.shift_set.get(pk=update['element_id'])

                else:
                    column = element.columns.get(name=update['column_name'])
                    child = column.rows.get(pk=update['element_id'])

                child.position = update['element_position']
                child.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'update_config':
            columns = data['value']

            config = RadiumConfig.objects.get(pk=data['element_id'])

            for column in columns:
                config_column = RadiumConfigColumn.objects.get(
                    pk=column['id'])

                for attr in ['id', 'name', 'config']:
                    del column[attr]

                for key, val in column.items():
                    if 'textsize' in key:
                        if not val or int(val) < 5:
                            val = 13

                    if 'width' in key:
                        if not val:
                            val = 100

                    setattr(config_column, key, val)

                config_column.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_parts':
            parts = list()

            for team_id in data['value']:
                part = Part.objects.create(
                    date=element.date,
                    team_id=team_id,
                    shift=element,
                )

                part_serialized = PartSerializer(part, context={
                    'parts': 'detail',
                    'profiles': 'detail',
                    'project': 'detail',
                }).data

                parts.append(part_serialized)

                day, c = Day.objects.get_or_create(
                    team_id=team_id, date=element.date)

                day.has_content = True
                day.save()

            return Response({'parts': parts})


        elif data['action'] == 'update_part':
            element.needs = data['value']['needs']
            element.locked = data['value']['locked']
            element.description = data['value']['description']

            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete_part':
            date = element.date
            profiles = [p for p in element.profiles.all()]
            part_team = element.team

            element.delete()

            self.set_day_cells_has_content(part_team, profiles, date)

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'create_part_profile_link':
            cell, c = Cell.objects.get_or_create(
                profile_id=data['profile_id'],
                date=element.date,
            )

            profile = Profile.objects.get(pk=data['profile_id'])

            link, c = PartProfileLink.objects.get_or_create(
                part=element,
                profile=profile,
            )

            profile_serialized = ProfileSerializer(profile).data
            profile_serialized['link'] = PartProfileLinkSerializer(
                link).data

            return Response({'profile': profile_serialized})


        elif data['action'] == 'update_part_profile_link':
            profile = Profile.objects.get(pk=data['profile_id'])

            link = PartProfileLink.objects.get(
                part=element,
                profile=profile,
            )

            is_participant = data['value']['is_participant'] \
                             and not link.is_participant

            is_not_participant = not data['value']['is_participant'] \
                                 and link.is_participant
            link.is_available = data['value']['is_available']
            link.is_participant = data['value']['is_participant']
            link.save()

            if is_participant:
                cell = Cell.objects.get(
                    profile_id=data['profile_id'],
                    date=element.date,
                )

                cell.has_content = True
                cell.save()

            if is_not_participant:
                cell = Cell.objects.get(
                    profile_id=data['profile_id'],
                    date=element.date,
                )

                has_child = self.cell_has_child(profile, cell)

                if not has_child:
                    cell.has_content = False
                    cell.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'part_override_short':
            links = PartProfileLink.objects.filter(
                part=element, is_participant=True)

            for link in links:
                cell, c = Cell.objects.get_or_create(
                    profile=link.profile, date=element.date)

                cell.short = data['value']
                cell.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'add_file':
            file = request.data['file']
            name = request.data['name']
            ext = request.data['ext']
            mini = None if 'mini' not in request.data else request.data['mini']

            directory = uuid.uuid4().hex
            file.filename = '{0}.{1}'.format(name, ext)

            if not ext:
                file.filename = '{0}'.format(name)

            path = '{0}/{1}'.format(directory, file.filename)

            default_storage.save(path, file)

            if mini:
                mini.filename = 'mini.{1}'.format(name, ext)
                path = '{0}/{1}'.format(directory, mini.filename)
                default_storage.save(path, mini)

            create_kwargs = {
                'kind': request.data['kind'],
                'name': request.data['name'],
                'extension': request.data['ext'],
                'uid': directory,
            }

            if 'width' in request.data:
                create_kwargs['width'] = request.data['width']
                create_kwargs['height'] = request.data['height']

            new_file = File.objects.create(**create_kwargs)
            file_serialized = FileSerializer(new_file).data

            work_file_link = WorkFileLink.objects.create(
                work=hierarchy['parent'],
                file=new_file,
                position=len(hierarchy['parent'].files.filter(
                    kind=request.data['kind'])),
            )

            file_serialized['link'] = WorkFileLinkSerializer(
                work_file_link).data

            return Response({'file': file_serialized})


        elif data['action'] == 'link_radiums':
            for app_id in data['value']:
                app = App.objects.get(pk=app_id)
                position = len(app.work_set.filter(date=element.date))

                app_work_link, c = AppWorkLink.objects.get_or_create(
                    app=app,
                    work=element,
                    position=position,
                    is_original=False,
                )

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'send_message':
            for app_id in request.data['app_ids']:
                app = App.objects.get(pk=app_id)

                message = Message.objects.create(
                    priority=request.data['priority'],
                    message=data['value'],
                    author=request.user.profile,
                    app=app,
                    work=element,
                )

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'acquit_message':
            message = Message.objects.get(pk=data['element_id'])
            message.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'move_work':
            link = AppWorkLink.objects.get(app=app, work=element)
            link.position = app.work_set.filter(date=data['date']).count()
            link.save()

            element.date = data['date']
            element.save()

            work_serialized = WorkSerializer(element, context={
                'files': 'detail',
                'shifts': 'detail',
                'apps': 'id',
            }).data

            work_serialized['link'] = AppWorkLinkSerializer(link).data

            return Response({
                'work': work_serialized,
            })


        elif data['action'] == 'copy_work':
            work_data = request.data['work']
            new_date = data['date']

            work = Work.objects.create(
                color=work_data['color'],
                date=data['date'],
            )

            works_in_month = app.work_set.filter(
                date=data['date'])
            position = len(works_in_month)

            link = AppWorkLink.objects.create(
                app=app,
                work=work,
                position=position,
                is_original=True,
            )

            keys_delete = ['id', 'created_date', 'updated_date',
                           'work', 'work_columns', 'work_column',
                           'is_edited', 'rows', ]

            for key, column in work_data['columns'].items():
                if 'id' in column:
                    rows = column['rows']

                    for key_delete in keys_delete:
                        if key_delete in column:
                            del column[key_delete]

                    work_column = WorkColumn.objects.create(
                        work=work, **column)

                    for row in rows:
                        for key_delete in keys_delete:
                            if key_delete in row:
                                del row[key_delete]

                        WorkRow.objects.create(work_column=work_column, **row)


            # TBD if its usefull to copy shifts aswell
            for shift in work_data['shifts']:
                Shift.objects.create(
                    date=shift['date'], 
                    shift=shift['shift'],
                    position=shift['position'],
                    work=work,
                )


            work_serialized = WorkSerializer(work, context={
                'files': 'detail',
                'shifts': 'detail',
                'apps': 'id',
            }).data

            work_serialized['link'] = AppWorkLinkSerializer(link).data

            return Response({
                'work': work_serialized,
            })


        return Response(status=status.HTTP_400_BAD_REQUEST)