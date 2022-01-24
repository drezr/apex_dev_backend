from apex.models import *

quotas = Quota.objects.all()
quotas_count = quotas.count()

for i, quota in enumerate(quotas):
    print ('\rChecking quota ({0}/{1})'.format(i, quotas_count), end="")

    same_quotas = Quota.objects.filter(
        profile=quota.profile, code=quota.code, year=quota.year)

    if same_quotas.count() > 1:
        print ('\nQuota double found ({0})\n'.format(quota))
        for same_quota in same_quotas.all():
            if same_quota.value == 0:
                same_quota.delete()
