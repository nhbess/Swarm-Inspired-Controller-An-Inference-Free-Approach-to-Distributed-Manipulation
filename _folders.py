import json
import os
import pickle

import torch.nn as nn
from loguru import logger


# DEFAULT FOLDER EXPERIMENT STRUCTURE
DEFAULT_FOLDERS = {
    'MODELS': '__Models',
    'SIMULATIONS': '__Simulations',
    'VISUALIZATIONS': '__Visualizations',
    'RESULTS': '__Results',
}

# FOLDER PATHS
MODELS_PATH =           None
SIMULATIONS_PATH =      None
VISUALIZATIONS_PATH =   None
RESULTS_PATH =          None

def _folder_paths() -> dict:
    paths = {}
    for key in DEFAULT_FOLDERS.keys():
        paths[key] = globals()[f'{key}_PATH']
    return paths

def _set_folders(configuration: dict = None):
    for key, value in DEFAULT_FOLDERS.items():
        globals()[f'{key}_PATH'] = value

    if configuration is not None:
        for key, value in configuration.items():
            if key not in DEFAULT_FOLDERS:
                raise Exception(f'DEFAULT_FOLDERS does not have the attribute {key}')
            globals()[f'{key}_PATH'] = value

def _create_folders():
    for folder_path in _folder_paths().values():
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

# Set default and configure if needed
_set_folders()
#create_folders()

def set_experiment_folders(experiment_name:str):
    if not os.path.exists(experiment_name):
        os.makedirs(experiment_name)

    _set_folders({
        'MODELS': f'{experiment_name}/{MODELS_PATH}',
        'SIMULATIONS': f'{experiment_name}/{SIMULATIONS_PATH}',
        'VISUALIZATIONS': f'{experiment_name}/{VISUALIZATIONS_PATH}',
        'RESULTS': f'{experiment_name}/{RESULTS_PATH}',
    })
    _create_folders()


def save_training_results(data, experiment_name):
    results = {'training_parameters': 0}
    results.update(data)

    result_path = os.path.join(RESULTS_PATH, f'{experiment_name}.json')
    print(f"Saving training results to path {result_path}")
    with open(result_path, 'w') as json_file:
        json.dump(results, json_file)



import os
import json
import gzip


def check_size():
    filename = 'test.json'
    limit_size = 1024 * 1024 * 100  # 100 MB

    if os.path.getsize(filename) > limit_size:
        with open(filename, 'rb') as f_in:
            data = json.load(f_in)
        with gzip.open(filename + '.gz', 'wb') as f_out:
            f_out.write(json.dumps(data).encode('utf-8'))
        os.remove(filename)
