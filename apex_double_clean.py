from apex.models import *


days = Day.objects.all()

for day in days:
    search = Day.objects.filter(team=day.team, date=day.date)

    if search.count() > 1:
        print(search)
        search[0].delete()


cells = Cell.objects.all()

for cell in cells:
    search = Cell.objects.filter(profile=cell.profile, date=cell.date)

    if search.count() > 1:
        print(search)
        search[0].delete()