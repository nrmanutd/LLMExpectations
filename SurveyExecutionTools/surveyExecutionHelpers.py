import json
from dataclasses import asdict
from pathlib import Path
from experimentsConfiguration import ExperimentsConfiguration


def saveExperimentConfiguration(cfg: ExperimentsConfiguration, resultsFolder: Path):
    resultsFolder.mkdir(parents=True, exist_ok=True)

    config_dict = asdict(cfg)

    file_path = resultsFolder/'configuration.txt'

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4, ensure_ascii=False)
