import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random
from Simulator import Simulator
import random
from Tile import Tile
from Behaviors import Behaviors
import json
import sys
import numpy as np
from TunableParameters import TunableParameters
from tqdm import tqdm

def simulate(shrink,threshold):
        TunableParameters.shrink_x = shrink
        TunableParameters.threshold_x_a = threshold
        
        setup_0['symbol'] = random.choice(["I", "O", "T", "J", "L", "S", "Z"])
        setup_0['resolution'] = 2
        simulator = Simulator(setup_0)
        results = simulator.run_simulation()
        return results

def loss_function(shrink,threshold):
    random.seed(0)
    np.random.seed(0)
    losses = []
    for i in tqdm(range(20)):
        results = simulate(shrink,threshold)
        coverage = results['coverage'][-1]
        if coverage == 0:
            coverage = 1e-5
        loss = 1/coverage
        losses.append(loss)
    loss = np.mean(losses)
    return loss

def visualize_results(file_path):
    with open(file_path, 'r') as f:
        results = json.load(f)
    
    shrinks = results['SHRINKS']
    thresholds = results['THRESHOLDS']
    losses = results['LOSSES']
    
    import matplotlib.pyplot as plt
   
    fig = plt.figure(figsize=(2.5,2.5))
    ax = fig.add_subplot(111)
    X = len(np.unique(shrinks))
    Y = len(np.unique(thresholds))    
    im = ax.imshow(np.array(losses).reshape((X,Y)), cmap='grey')
    #add axis titles
    ax.set_xticks(np.arange(X))
    ax.set_yticks(np.arange(Y))
    ax.set_xticklabels(round(a,2) for a in np.unique(shrinks))
    ax.set_yticklabels(round(a,2) for a in np.unique(thresholds))
    #rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlabel(f'Decay factor $\mu$')
    ax.set_ylabel('Threshold $th$')
    
    plt.scatter(0.5*10-0.5,0.16*10, color='w', marker='x',s=100, label='Optimal parameters')

    plt.savefig(f'Images/Paper/Parameters.png', bbox_inches='tight', dpi=300)
    #plt.show()


if __name__ == "__main__":

    import _folders
    _folders.set_experiment_folders('_Optimization')
    Tile.execute_behavior = Behaviors.behavior_swarmy_rotation

    file_path = f'{_folders.RESULTS_PATH}/Optimization_Grid_Search.json'
    visualize_results(file_path)
    

    #Optima parameters:
    #Shrink: 0.5
    #Threshold: 0.16
   
    sys.exit()

    
    setup_0 = {
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
        'data_tiles': True,
        'data_objet_target': True,
        'file_name': False,

        'dead_tiles': 0,
        'save_animation': False,
        'max_iterations': 600,
    }
    
    n = 10
    shrinks     = np.linspace(0.25,0.45,n)
    thresholds  = np.linspace(0.8,1,n)
    
    print(f"Shrinks: {shrinks}")
    print(f"Thresholds: {thresholds}")

    results = {
        'SHRINKS': [],
        'THRESHOLDS': [],
        'LOSSES': []
    }
    
    counter = n**2

    for shrink in tqdm(shrinks):
        for threshold in tqdm(thresholds):
        
            loss = loss_function(shrink,threshold)
            
            results['SHRINKS'].append(shrink)
            results['THRESHOLDS'].append(threshold)
            results['LOSSES'].append(loss)
            
            counter -= 1
            print(f"To test: {counter}, Loss: {loss}, Params: {shrink,threshold}")
    
    file_path = f'{_folders.RESULTS_PATH}/Optimization_Grid_Search_Fine_Tunning.json'
    with open(file_path, 'w') as f:
        json.dump(results, f)

    visualize_results(file_path)
    sys.exit()