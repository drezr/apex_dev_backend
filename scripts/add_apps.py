from apex.models import *

team_ids = [128, 129, 130, 131, 132, 133, 134, 135]

for team_id in team_ids:
	for app_name in ['draft', 'planner', 'radium', 'watcher']:

		App.objects.create(
			app=app_name,
			team_id=team_id,
		)
