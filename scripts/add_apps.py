from apex.models import *

team_ids = [136, 137]

for team_id in team_ids:
	for app_name in ['draft', 'planner', 'radium', 'watcher']:

		App.objects.create(
			app=app_name,
			team_id=team_id,
		)
