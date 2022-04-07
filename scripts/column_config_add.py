from apex.models import *
from apex.default_configs.radium_default_config import radium_default_config



print('Adding new columns...')


configs = RadiumConfig.objects.all()

for config in configs:
	config_columns = RadiumConfigColumn.objects.filter(config=config)

	for default_config in radium_default_config:
		exist = False

		for config_column in config_columns:
			if default_config['name'] == config_column.name:
				exist = True

		if not exist:
			RadiumConfigColumn.objects.create(
				config=config,
				name=default_config['name'],
				position=default_config['position'],
				width=default_config['width'],
				textsize=default_config['textsize'],
				visible=default_config['visible'],
				multiple=default_config['multiple'],
				clickable=default_config['clickable'],
				path=default_config['path'],
			)


print('Done.')