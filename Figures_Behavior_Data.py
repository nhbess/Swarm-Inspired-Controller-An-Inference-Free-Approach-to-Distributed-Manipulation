import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random
from Simulator import Simulator
import random
from Tile import Tile
from Behaviors import Behaviors
import json
import sys

if __name__ == "__main__":
    sys.exit()
    seed = random.randint(0, 1000000)    
    random.seed(617986)
    print(f'Random seed: {seed}')

    Tile.execute_behavior = Behaviors.information_diffusion
    Tile.execute_behavior = Behaviors.behavior_swarmy_rotation

    setup_0 = {
        'N' : 20,
        'TILE_SIZE' : 20,
        'object': True,
        'symbol': 'T',
        'target_shape': True,
        'show_tetromines' : False,
        'show_tetromino_contour' : True,
        
        'resolution': 5,

        'n_random_targets' : 0,
        'shuffle_targets': False,
        
        'delay': False,
        'visualize': True,

        'save_data': True,
        'data_tiles': True,
        'data_objet_target': True,
        'file_name': False,

        'dead_tiles': 0,
        'save_animation': False,
        'max_iterations': 1000,
    }
    
    symbol = random.choice(["O", "L","J", "S", "Z"])
    setup_0['symbol'] = 'L'
    setup_0['resolution'] = 2
    simulator = Simulator(setup_0)

    data = simulator.run_simulation(save_sys_data=True)
    
    results_path = f'Images\Data\Data_Behavior.json'
    with open(results_path, 'w') as file:
        json.dump(data, file, indent=4)