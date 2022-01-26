from apex.models import *

works = Work.objects.all()

for work in works:
    columns = WorkColumn.objects.filter(
        work=work,
        name='limits',
    )

    if columns.count() > 1:
        kept_column = columns[0]

        for i, column in enumerate(columns.all()):
            if i > 0:
                for row in column.rows.all():
                    print('Merging row #' + str(row.id))
                    row.work_column = kept_column
                    row.position = i
                    row.save()

                print('Deleting column #' + str(column.id))
                column.delete()