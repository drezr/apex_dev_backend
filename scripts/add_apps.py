from apex.models import *

team_ids = [116, 117, 118, 119, 120, 121, 122, 123]

for team_id in team_ids:
	for app_name in ['draft', 'planner', 'radium', 'watcher']:

		App.objects.create(
			app=app_name,
			team_id=team_id,
		)