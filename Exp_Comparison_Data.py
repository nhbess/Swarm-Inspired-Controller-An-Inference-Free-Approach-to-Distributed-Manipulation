import random
from Simulator import Simulator
from Tile import Tile
from Behaviors import Behaviors
import json
import _config
from tqdm import tqdm
import sys
if __name__ == '__main__':
    sys.exit()
    import _folders
    experiment_name = '_Comparison'
    _folders.set_experiment_folders(experiment_name)

    setup = {
        'N' : 20,
        'TILE_SIZE' : 20,
        'object': True,
        'symbol': 'T',
        'target_shape': True,
        'show_tetromines' : False,
        'show_tetromino_contour' : True,
        
        'resolution': 2,

        'n_random_targets' : 0,
        'shuffle_targets': False,
        
        'delay': False,
        'visualize': False,

        'save_data': True,
        'data_tiles': False,
        'data_objet_target': True,
        'file_name': 'defaultname',

        'dead_tiles': 0,
        'save_animation': False,
        'max_iterations': 1000,
    }

    behaviors = [Behaviors.information_diffusion, Behaviors.behavior_swarmy_rotation]
    behaviors_names = [_config.INFORMATION_DIFFUSION_NAME, _config.SWARMY_NAME]
    
    symbols = ["I", "O", "T", "J", "L", "S", "Z"]

    runs_per_behavior = 100

    results = {}
    for behavior, behaviors_name in tqdm(zip(behaviors, behaviors_names)):
        Tile.execute_behavior = behavior
        results[behaviors_name] = []
        
        for run in tqdm(range(runs_per_behavior)):
            setup['symbol'] = random.choice(symbols)
            simulator = Simulator(setup)
            run_data = simulator.run_simulation()
            results[behaviors_name].append(run_data)

    results_path = f'{_folders.RESULTS_PATH}/results.json'
    with open(results_path, 'w') as file:
        json.dump(results, file, indent=4)        
    
    
