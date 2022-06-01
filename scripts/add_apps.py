from apex.models import *

team_ids = [
	138,
	139,
	140,
	141,
	142,
	143,
	144,
	145,
	146,
	147,
	148,
	149,
]

for team_id in team_ids:
	for app_name in ['draft', 'planner', 'radium', 'watcher']:

		App.objects.create(
			app=app_name,
			team_id=team_id,
		)
