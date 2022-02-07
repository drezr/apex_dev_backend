from .models import *
from .serializers import *
from .quota import compute_quota


def days_to_cats(days, team, app, month, year):
    result = list()

    for day in days:
        for task in day.tasks.all():
            if task.codes.count():
                links = CellTaskLink.objects.filter(task=task)
                profiles = [link.cell.profile for link in links]

                for code in task.codes.all():
                    for profile in profiles:
                        result.append({
                            'name': profile.name,
                            'ident': profile.ident.replace(' ', '').replace('-', ''),
                            'date': day.date.strftime('%Y-%m-%d'),
                            'presence': code.presence,
                            'hour': code.hour,
                            'start': code.start,
                            'end': code.end,
                            'work': code.work,
                            'place': code.place,
                            'project': code.project,
                            'other': code.other,
                            'network': code.network,
                            'activity': code.activity,
                        })

    watcher = team.app_set.filter(app='watcher').first()

    leave_kinds = [
        'counter_special',
        'counter_unjustified',
        'counter_strike',
        'counter_wounded',
        'normal_leave',
        'credit_day',
        'variable_leave',
        'saturday',
        'sunday',
        'holiday',
        'hour',
    ]

    leave_codes = {
        'counter_special': '0004',
        'counter_unjustified': '0068',
        'counter_strike': '0065',
        'counter_wounded': '????',
        'normal_leave': '0007',
        'credit_day': '0030',
        'variable_leave': '0022',
        'saturday': '0021',
        'sunday': '0001',
        'holiday': '0002',
        'hour': '0023',
    }

    if watcher:
        config, c = LeaveConfig.objects.get_or_create(app=watcher)
        leave_config = LeaveConfigSerializer(config).data
        holidays = Holiday.objects.filter(date__month=month, date__year=year)
        holidays = HolidaySerializer(holidays, many=True).data
        leave_types = config.leave_type_set.all()

        for profile in team.profiles.all():
            link = TeamProfileLink.objects.get(team=team, profile=profile)

            if link.watcher_is_visible:
                quotas = Quota.objects.filter(
                    profile=profile, year=year)
                cells = Cell.objects.filter(
                    date__year=year, profile=profile)

                base_quotas, computed_quotas, detailed_quotas = compute_quota(
                    cells=CellSerializer(cells, many=True).data,
                    quotas=QuotaSerializer(quotas, many=True).data,
                    config=leave_config,
                    holidays=holidays,
                    detailed=True,
                )

                for quota in detailed_quotas:
                    if detailed_quotas[quota]:
                        for leave_type in leave_types:
                            if quota == leave_type.code.lower():
                                if leave_type.kind in leave_kinds:
                                    for entry in detailed_quotas[quota]:
                                        amount = float(entry['count'])
                                        amount = int(amount) if isinstance(amount, float) and amount.is_integer() else round(amount, 2)

                                        if amount < 0:
                                            amount = -amount

                                            if leave_type.kind != 'hour':
                                                amount = amount * 8

                                            result.append({
                                                'name': profile.name,
                                                'ident': profile.ident.replace(' ', '').replace('-', ''),
                                                'date': entry['date'],
                                                'presence': leave_codes[leave_type.kind],
                                                'hour': amount,
                                                'start': '',
                                                'end': '',
                                                'work': '',
                                                'place': '',
                                                'project': '',
                                                'other': '',
                                                'network': '',
                                                'activity': '',
                                            })

    print(result)