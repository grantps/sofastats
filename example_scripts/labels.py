from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)
try:
    data_label_mappings = yaml.load(Path.cwd() / 'data_labels.yaml')  ## might be a str or Path so make sure
except FileNotFoundError:
    data_label_mappings = {}
