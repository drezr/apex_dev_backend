import shutil
import uuid

from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..permissions import *


class ElementView(APIView, ElementHelpers, Helpers):

    def get_child_count(self, data, element, hierarchy, option='all'):
        count = 0

        if option == 'all' or option == 'exclude_calls':
            if data['parent_type'] not in ['task', 'call']:
                count += len(hierarchy[element].tasks.all())

            if data['parent_type'] == 'task':
                count += len(hierarchy[element].inputs.all())
                count += len(hierarchy[element].codes.all())

            if data['parent_type'] in ['task', 'folder', 'day', 'cell']:
                count += len(hierarchy[element].notes.all())
                count += len(hierarchy[element].files.all())

        if option == 'all' or option == 'only_calls':
            if data['parent_type'] == 'cell':
                count += len(hierarchy[element].calls.all())


        if option == 'all' or option == 'exclude_calls':
            if data['parent_type'] == 'day':
                parts = Part.objects.filter(
                    team=hierarchy['team'], date=hierarchy['parent'].date)

                count += len(parts)

            elif data['parent_type'] == 'cell':
                parts = Part.objects.filter(
                    team=hierarchy['team'], date=hierarchy['parent'].date)

                for part in parts:
                    links = PartProfileLink.objects.filter(
                        part=part,
                        profile=hierarchy[element].profile,
                        is_participant=True,
                    )

                    count += len(links)


        return count


    def post(self, request):
        create_kwargs = dict()
        link_kwargs = dict()
        element_serialized = None

        data, hierarchy, permission = self.get_data(request)

        if not permission:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        if data['action'] == 'create':
            if data['element_type'] in ['task', 'subtask']:
                create_kwargs = {'status': 'pending'}

            elif data['element_type'] == 'input':
                create_kwargs = {'kind': data['kind']}

            elif data['element_type'] == 'link':
                create_kwargs = {'url': data['url'], 'name': data['name']}

            elif data['element_type'] == 'note':
                create_kwargs = {'profile': request.user.profile}

            elif data['element_type'] == 'file':
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


            element = hierarchy['element_model'].objects.create(
                **create_kwargs)
            element_serialized = hierarchy['element_serializer'](
                element, context={
                    'tasks': 'detail',
                    'subtasks': 'detail',
                    'inputs': 'detail',
                    'notes': 'detail',
                    'files': 'detail',
                    'calls': 'detail',
                    'links': 'detail',
                    'codes': 'detail',
                    'teammates': 'detail',
                }).data

            link_kwargs[data['parent_type']] = hierarchy['parent']
            link_kwargs[data['element_type']] = element
            link_kwargs['position'] = self.get_child_count(
                data, 'parent', hierarchy) + 1
            link_kwargs['is_original'] = True

            link = hierarchy['link_model'].objects.create(**link_kwargs)
            element_serialized['link'] = hierarchy['link_serializer'](
                link).data

            if data['parent_type'] in ['day', 'cell']:
                if data['element_type'] == 'call':
                    hierarchy['parent'].has_call = True

                else:
                    hierarchy['parent'].has_content = True

                hierarchy['parent'].save()


            if data['view'] == 'project' and data['element_type'] == 'task':
                if hierarchy['app'].template:
                    template = TaskSerializer(
                        hierarchy['app'].template, context={
                            'link': 'detail',
                            'subtasks': 'detail',
                            'inputs': 'detail',
                            'notes': 'detail',
                            'codes': 'detail',
                        }).data

                    for child_type in ['note', 'subtask', 'input', 'code']:
                        children = template[child_type + 's']

                        for child in children:
                            child_model = globals()[child_type.capitalize()]
                            link_model = globals()[
                                'Task' + child_type.capitalize() + 'Link']

                            new_child = None
                            new_link_args = dict()

                            if child_type == 'note':
                                new_child = child_model.objects.create(
                                    value=child['value'],
                                    profile=request.user.profile,
                                )

                                new_link_args

                            elif child_type == 'subtask':
                                new_child = child_model.objects.create(
                                    name=child['name'],
                                    status=child['status'],
                                )

                            elif child_type == 'input':
                                new_child = child_model.objects.create(
                                    kind=child['kind'],
                                    key=child['key'],
                                    value=child['value'],
                                    heading=child['heading'],
                                )

                            elif child_type == 'code':
                                new_child = child_model.objects.create(
                                    presence=child['presence'],
                                    place=child['place'],
                                    work=child['work'],
                                    project=child['project'],
                                    other=child['other'],
                                )

                            new_link_args['task'] = element
                            new_link_args[child_type] = new_child
                            new_link_args['position'] = child['link']['position']

                            new_link = link_model.objects.create(
                                **new_link_args)

                            element_serialized = hierarchy['element_serializer'](
                                element, context={
                                    'link': 'detail',
                                    'subtasks': 'detail',
                                    'inputs': 'detail',
                                    'notes': 'detail',
                                    'files': 'detail',
                                    'calls': 'detail',
                                    'links': 'detail',
                                    'codes': 'detail',
                                    'teammates': 'detail',
                                }).data

                            element_serialized['link'] = hierarchy['link_serializer'](link).data

            result = {
                data['element_type']: element_serialized,
            }

            return Response(result)


        elif data['action'] == 'update':
            element = hierarchy['element']

            if data['element_type'] == 'file':
                media = default_storage.location
                old_path = None
                new_path = None

                if element.extension:
                    old_path = '{0}/{1}/{2}.{3}'.format(
                        media, element.uid, element.name, element.extension)
                    new_path = '{0}/{1}/{2}.{3}'.format(
                        media, element.uid, data['name'], element.extension)

                else:
                    old_path = '{0}/{1}/{2}'.format(
                        media, element.uid, element.name)
                    new_path = '{0}/{1}/{2}'.format(
                        media, element.uid, data['name'])

                if old_path != new_path:
                    shutil.move(old_path, new_path)


            updatable_fields = [
                'name',
                'key',
                'value',
                'heading',
                'status',
                'kind',
                'start',
                'end',
                'description',
                'url',
                'presence',
                'work',
                'place',
                'project',
                'other',
                'network',
                'activity',
            ]

            for field in updatable_fields:
                if data[field]:
                    setattr(element, field, data[field])


            element.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'delete':
            link_kwargs[data['parent_type']] = hierarchy['parent']
            link_kwargs[data['element_type']] = hierarchy['element']

            link = hierarchy['link_model'].objects.get(**link_kwargs)
            element = hierarchy['element']

            possible_children = {
                'task': ['note', 'file', 'input', 'subtask', 'code'],
                'call': ['file', 'link'],
            }

            if data['parent_type'] in ['day', 'cell']:
                if data['element_type'] == 'call':
                    count = self.get_child_count(
                        data, 'parent', hierarchy, 'only_calls')

                    if count <= 1:
                        hierarchy['parent'].has_call = False

                else:
                    count = self.get_child_count(
                        data, 'parent', hierarchy, 'exclude_calls')

                    if count <= 1:
                        hierarchy['parent'].has_content = False


                    cell_link_model = globals()[
                        'Cell' +
                        data['element_type'].capitalize() + 'Link']

                    cell_link_kwargs = dict()
                    cell_link_kwargs[data['element_type']] = hierarchy['element']

                    cell_links = cell_link_model.objects.filter(
                        **cell_link_kwargs
                    )

                    for cell_link in cell_links:
                        cell = cell_link.cell

                        child_count = self.cell_child_count(cell.profile, cell)

                        if child_count == 1:
                            cell.has_content = False
                            cell.save()

                
                hierarchy['parent'].save()

            if link.is_original:
                for element_type in possible_children:
                    if data['element_type'] == element_type:
                        for child_type in possible_children[element_type]:
                            child_set = getattr(element, child_type + 's')

                            for child in child_set.all():
                                if child_type == 'file':
                                    path = '{0}/{1}/'.format(
                                        default_storage.location, child.uid)
                                    shutil.rmtree(path)


                                child.delete()


                if data['element_type'] == 'file':
                    path = '{0}/{1}/'.format(
                        default_storage.location, element.uid)
                    shutil.rmtree(path)


                element.delete()

            else:
                link.delete()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'position':
            element = hierarchy['element']

            for child_data in data['position_updates']:
                link_kwargs = dict()

                child_set = getattr(element, child_data['element_type'] + 's')
                child = child_set.get(pk=child_data['element_id'])

                link_model = globals()[
                    data['element_type'].capitalize() +
                    child_data['element_type'].capitalize() + 'Link']

                link_kwargs[child_data['element_type']] = child
                link_kwargs[data['element_type']] = hierarchy['element']

                link = link_model.objects.get(**link_kwargs)

                if link:
                    link.position = child_data['position']
                    link.save()

            return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'move':
            old_link_kwargs = dict()
            new_link_kwargs = dict()

            old_link_kwargs[data['parent_type']] = hierarchy['parent']
            old_link_kwargs[data['element_type']] = hierarchy['element']
            new_link_kwargs[data['new_parent_type']] = hierarchy['new_parent']
            new_link_kwargs[data['element_type']] = hierarchy['element']

            old_link = hierarchy['link_model'].objects.get(**old_link_kwargs)
            new_link, c = hierarchy['new_link_model'].objects.get_or_create(
                **new_link_kwargs)

            cell_link_model = globals()[
                'Cell' + data['element_type'].capitalize() + 'Link']

            cell_link_kwargs = dict()
            cell_link_kwargs[data['element_type']] = hierarchy['element']
            cell_links = cell_link_model.objects.filter(**cell_link_kwargs)

            if old_link and new_link:
                if old_link == new_link:
                    setattr(old_link, data['parent_type'],
                            hierarchy['new_parent'])
                    old_link.save()

                else:
                    old_link.delete()

                    setattr(new_link, data['new_parent_type'],
                            hierarchy['new_parent'])
                    new_link.save()

                    if data['parent_type'] == 'day':
                        parent_child_count = self.get_child_count(
                            data, 'parent', hierarchy, 'exclude_calls')

                        if parent_child_count == 0:
                            hierarchy['parent'].has_content = False
                            hierarchy['parent'].save()

                    if data['new_parent_type'] == 'day':
                        hierarchy['new_parent'].has_content = True
                        hierarchy['new_parent'].save()

                        day_serialized = DaySerializer(
                            hierarchy['new_parent'], context={
                                'link': 'detail',
                                'tasks': 'detail',
                                'subtasks': 'detail',
                                'inputs': 'detail',
                                'notes': 'detail',
                                'files': 'detail',
                                'links': 'detail',
                                'codes': 'detail',
                                'teammates': 'detail',
                            }).data

                        # day_serialized['link'] = \
                        #     hierarchy['new_link_serializer'](new_link).data


                        for cell_link in cell_links:
                            old_cell = cell_link.cell
                            new_cell, c = Cell.objects.get_or_create(
                                profile=old_cell.profile,
                                date=hierarchy['new_parent'].date
                            )

                            new_cell.has_content = True
                            new_cell.save()

                            cell_link.cell = new_cell

                            child_count = self.cell_child_count(
                                new_cell.profile, new_cell)

                            cell_link.position = child_count

                            cell_link.save()

                            has_child = self.cell_has_child(
                                old_cell.profile, old_cell)

                            if not has_child:
                                old_cell.has_content = False
                                old_cell.save()


                        result = {
                            'day': day_serialized,
                        }

                        return Response(result)


                    if data['new_parent_type'] == 'folder':
                        for cell_link in cell_links:
                            cell = cell_link.cell
                            cell_link.delete()

                            child_count = self.cell_child_count(
                                cell.profile, cell)

                            if child_count == 0:
                                cell.has_content = False
                                cell.save()


                    if data['new_parent_type'] == 'project':
                        element_serialized = TaskSerializer(
                            hierarchy['element'], context={
                                'link': 'detail',
                                'subtasks': 'detail',
                                'inputs': 'detail',
                                'notes': 'detail',
                                'files': 'detail',
                                'calls': 'detail',
                                'links': 'detail',
                                'codes': 'detail',
                                'teammates': 'detail',
                            }).data

                        element_serialized['link'] = ProjectTaskLinkSerializer(
                            new_link).data

                        return Response({'task': element_serialized})


                    if data['element_type'] == 'call':
                        call_count = hierarchy['parent'].calls.all().count()

                        if call_count == 0:
                            hierarchy['parent'].has_call = False
                            hierarchy['parent'].save()

                        hierarchy['new_parent'].has_call = True
                        hierarchy['new_parent'].save()

                        element_serialized = CallSerializer(
                            hierarchy['element'], context={
                                'link': 'detail',
                                'files': 'detail',
                                'links': 'detail',
                                'teammates': 'detail',
                            }).data

                        element_serialized['link'] = CellCallLinkSerializer(
                            new_link).data

                        return Response({'call': element_serialized})


                return Response(status=status.HTTP_200_OK)


        elif data['action'] == 'copy':
            original = hierarchy['element_model'].objects.get(
                pk=data['element_id'])

            new_element = original
            new_element.pk = None
            new_element.save()

            original = hierarchy['element_model'].objects.get(
                pk=data['element_id'])

            if data['element_type'] == 'task':
                for subtask in original.subtasks.all():
                    new_subtask = Subtask.objects.create(
                        name=subtask.name, status=subtask.status)
                    link = TaskSubtaskLink.objects.get(
                        task=original, subtask=subtask)
                    TaskSubtaskLink.objects.create(
                        task=new_element, subtask=new_subtask, position=link.position)

                for note in original.notes.all():
                    new_note = Note.objects.create(
                        value=note.value, profile=note.profile)
                    link = TaskNoteLink.objects.get(
                        task=original, note=note)
                    TaskNoteLink.objects.create(
                        task=new_element, note=new_note, position=link.position)

                for _input in original.inputs.all():
                    new_input = Input.objects.create(
                        kind=_input.kind, key=_input.key,
                        value=_input.value, heading=_input.heading)
                    link = TaskInputLink.objects.get(
                        task=original, input=_input)
                    TaskInputLink.objects.create(
                        task=new_element, input=new_input, position=link.position)

                for code in original.codes.all():
                    new_code = Code.objects.create(
                        presence=code.presence,
                        place=code.place,
                        work=code.work,
                        project=code.project,
                        other=code.other,
                    )
                    link = TaskCodeLink.objects.get(
                        task=original, code=code)
                    TaskCodeLink.objects.create(
                        task=new_element, code=new_code, position=link.position)


            position = 0

            position += hierarchy['new_parent'].tasks.all().count()

            if data['new_parent_type'] != 'project':
                position += hierarchy['new_parent'].notes.all().count()
                position += hierarchy['new_parent'].files.all().count()

            if data['new_parent_type'] == 'day':
                parts = Part.objects.filter(
                team=hierarchy['team'], date=hierarchy['new_parent'].date)

                position += len(parts)

            if data['parent_type'] == 'day' and data['view'] == 'board':
                cell_links = None
                
                if data['element_type'] == 'task':
                    cell_links = CellTaskLink.objects.filter(
                        task=original)
                
                elif data['element_type'] == 'note':
                    cell_links = CellNoteLink.objects.filter(
                        note=original)

                if data['new_parent_type'] != 'folder':
                    for cell_link in cell_links:
                        cell, c = Cell.objects.get_or_create(
                            date=hierarchy['new_parent'].date,
                            profile=cell_link.cell.profile,
                        )

                        cell.has_content = True
                        cell.save()

                        if data['element_type'] == 'task':
                            CellTaskLink.objects.create(
                                cell=cell, task=new_element)
                        
                        elif data['element_type'] == 'note':
                            CellNoteLink.objects.create(
                                cell=cell, note=new_element)


            link_kwargs = dict()
            link_kwargs[data['new_parent_type']] = hierarchy['new_parent']
            link_kwargs[data['element_type']] = new_element
            link_kwargs['position'] = position

            link = hierarchy['new_link_model'].objects.create(**link_kwargs)

            element_serialized = hierarchy['element_serializer'](
                new_element, context={
                    'link': 'detail',
                    'subtasks': 'detail',
                    'inputs': 'detail',
                    'notes': 'detail',
                    'files': 'detail',
                    'calls': 'detail',
                    'links': 'detail',
                    'codes': 'detail',
                    'teammates': 'detail',
                }).data

            element_serialized['link'] = hierarchy['new_link_serializer'](link).data

            result = {
                data['element_type']: element_serialized,
            }

            if data['new_parent_type'] == 'day':
                hierarchy['new_parent'].has_content = True
                hierarchy['new_parent'].save()

                result['day'] = DaySerializer(
                    hierarchy['new_parent'], context={
                        'link': 'detail',
                        'tasks': 'detail',
                        'subtasks': 'detail',
                        'inputs': 'detail',
                        'notes': 'detail',
                        'files': 'detail',
                        'links': 'detail',
                        'codes': 'detail',
                        'teammates': 'detail',
                    }).data


            if data['new_parent_type'] == 'cell':
                #TO BE CHECKED
                if data['element_type'] == 'call':
                    hierarchy['new_parent'].has_call = True

                else:
                    hierarchy['new_parent'].has_content = True

                hierarchy['new_parent'].save()

                result['cell'] = CellSerializer(
                    hierarchy['new_parent'], context={
                        'link': 'detail',
                        'tasks': 'detail',
                        'subtasks': 'detail',
                        'inputs': 'detail',
                        'notes': 'detail',
                        'files': 'detail',
                        'links': 'detail',
                        'codes': 'detail',
                        'teammates': 'detail',
                    }).data

            return Response(result)


        return Response(status=status.HTTP_400_BAD_REQUEST)