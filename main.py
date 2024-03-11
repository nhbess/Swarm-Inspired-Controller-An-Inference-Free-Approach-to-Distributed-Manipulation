import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random
from Simulator import Simulator
import random
from Tile import Tile
from Behaviors import Behaviors

if __name__ == "__main__":
    seed = random.randint(0, 1000000)    
    random.seed(87716)
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

        'save_data': False,
        'data_tiles': False,
        'data_objet_target': True,
        'file_name': False,

        'dead_tiles': 0,
        'save_animation': False,
        'max_iterations': 1000,
    }
    
    
    
    symbol = random.choice(["I", "O", "T", "J", "L", "S", "Z"])
    setup_0['symbol'] = symbol
    setup_0['resolution'] = 2
    simulator = Simulator(setup_0)
    simulator.run_simulation()