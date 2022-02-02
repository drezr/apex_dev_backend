from apex.models import *



print('### Cleaning doubles ###')

print('\n--- Cleaning day doubles')

days = Day.objects.all()
days_count = days.count()

for i, day in enumerate(days):
    print ('\rChecking day double ({0}/{1})'.format(i, days_count), end="")

    search = Day.objects.filter(team=day.team, date=day.date)

    if search.count() > 1:
        print ('\nFound double ({0})\n'.format(search[0]))
        search[0].delete()



print('\n--- Cleaning cell doubles')

cells = Cell.objects.all()
cells_count = cells.count()

for i, cell in enumerate(cells):
    print ('\rChecking cell double ({0}/{1})'.format(i, cells_count), end="")

    search = Cell.objects.filter(profile=cell.profile, date=cell.date)

    if search.count() > 1:
        print ('\nFound double ({0})\n'.format(search[0]))
        search[0].delete()



print('\n--- Cleaning part doubles')

parts = Part.objects.all()
parts_count = parts.count()

for i, part in enumerate(parts):
    print ('\rCleaning part double ({0}/{1})'.format(i, parts_count), end="")

    same_parts = Part.objects.filter(team=part.team, shift=part.shift)

    if same_parts.count() > 1:
        part_has_link = None

        for same_part in same_parts:
            has_link = PartProfileLink.objects.filter(part=same_part).count()

            if has_link:
                part_has_link = same_part


        if part_has_link:
            for same_part in same_parts:
                if same_part != part_has_link:
                    print ('\nFound double ({0})\n'.format(same_part))
                    same_part.delete()


        else:
            for same_part in same_parts:
                if same_part is not same_parts[0]:
                    print ('\nFound double ({0})\n'.format(same_part))
                    same_part.delete()



print('\n--- Cleaning quota doubles')

quotas = Quota.objects.all()
quotas_count = quotas.count()

for i, quota in enumerate(quotas):
    print ('\rChecking quota ({0}/{1})'.format(i, quotas_count), end="")

    same_quotas = Quota.objects.filter(
        profile=quota.profile, code=quota.code, year=quota.year)

    if same_quotas.count() > 1:
        print ('\nFound double ({0})\n'.format(quota))
        for same_quota in same_quotas.all():
            if same_quota.value == 0:
                same_quota.delete()

print('')