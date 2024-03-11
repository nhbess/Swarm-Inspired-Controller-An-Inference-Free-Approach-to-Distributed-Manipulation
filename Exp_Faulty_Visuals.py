import json
import os

import matplotlib.pyplot as plt
import numpy as np

import _colors
import _folders
import gzip
import sys

experiment_name=f'_Fault_Tolerance'
_folders.set_experiment_folders(experiment_name)

def _correct_behavior_name(behavior):
    if behavior == 'Information Diffusion':
        return behavior
    if behavior == 'Swarmy':
        return 'Swarm Inspired'

def _get_results():
    experiment_files = [f for f in os.listdir(_folders.RESULTS_PATH) if f.endswith('.json') or f.endswith('.gz')]
    print(experiment_files)
    exp_file = experiment_files[0]
    exp_path = os.path.join(_folders.RESULTS_PATH, exp_file)

    for exp in experiment_files:
        exp_path = os.path.join(_folders.RESULTS_PATH, exp)
        
        if exp.endswith('.gz'):
            with gzip.open(exp_path, 'rb') as file:
                exp_data = json.load(file)
                exp = exp.replace('.gz', '')
        else:
            with open(exp_path, 'r') as file:
                exp_data = json.load(file)
    
    results = {}

    for behavior in exp_data:
        data_behavior = exp_data[behavior]
        target_centers = np.array([run['TARGET_CENTER'] for run in data_behavior])
        target_angles = np.array([run['TARGET_ANGLE'] for run in data_behavior])
        tile_sizes = np.array([run['TILE_SIZE'] for run in data_behavior])
        dead_tiles = np.array([run['DEAD_TILES'] for run in data_behavior])
        shapes = np.array([run['SHAPE'] for run in data_behavior])

        #Correcting for distance
        final_object_centers = np.array([[run['object_center_x'][-1],run['object_center_y'][-1]] for run in data_behavior])
        resultant_distance_error = np.linalg.norm(target_centers - final_object_centers, axis=1)/ tile_sizes
        
        #Correction for angles
        final_object_angles = np.array([run['object_angle'][-1] for run in data_behavior])
        final_object_angles = final_object_angles % 360
        target_angles = target_angles % 360
        
        final_object_angles = np.where(final_object_angles > 180, 360 - final_object_angles, final_object_angles)
        target_angles = np.where(target_angles > 180, 360 - target_angles, target_angles)
        resultant_angle_error = abs(target_angles - final_object_angles)


        #Symmetry free error
        symmetry = {"I": 180, 
                   "O": 90, 
                   "T": 360, 
                   "J": 360, 
                   "L": 360, 
                   "S": 180, 
                   "Z": 180}


        symmetry_free_angle_error = []
        for i, shape in enumerate(shapes):
            symmetry_free_angle_error.append(min(abs(symmetry[shape] - resultant_angle_error[i]), resultant_angle_error[i]))
        
        symmetry_free_angle_error = np.array(symmetry_free_angle_error)
       
        shapes_errors = {}
        for i, shape in enumerate(shapes):
            if shape not in shapes_errors:
                shapes_errors[shape] = {'distance_error': [], 'angle_error': []}
            shapes_errors[shape]['distance_error'].append(resultant_distance_error[i])
            shapes_errors[shape]['angle_error'].append(resultant_angle_error[i])


        results[behavior] = {
            'distance_error': resultant_distance_error,
            'angle_error': resultant_angle_error,
            'dead_tiles': dead_tiles,
            'symmetry_free_angle_error': symmetry_free_angle_error
        }
    return results



def resultant_error():
    results = _get_results()

    results_by_dead_tile = {}

    for behavior in results:
        dead_tiles = results[behavior]['dead_tiles']
        dead_tiles = np.unique(dead_tiles)
        dead_tiles = np.sort(dead_tiles)

        results_by_dead_tile[behavior] = {
            'dead_tiles': dead_tiles,
            'error_d_means': [],
            'error_a_means': [],
            'error_sa_means': [],
            'error_d_std': [],
            'error_a_std': [],
            'error_sa_std': [],
        }
        for dead_tile in dead_tiles:
            mask = results[behavior]['dead_tiles'] == dead_tile
            distance_error = results[behavior]['distance_error'][mask]
            angle_error = results[behavior]['angle_error'][mask]
            sangle_error = results[behavior]['symmetry_free_angle_error'][mask]

            mean_distance_error = np.mean(distance_error)
            mean_angle_error = np.mean(angle_error)
            mean_sangle_error = np.mean(sangle_error)
            std_distance_error = np.std(distance_error)
            std_angle_error = np.std(angle_error)
            std_sangle_error = np.std(sangle_error)
            
            results_by_dead_tile[behavior]['error_d_means'].append(mean_distance_error)
            results_by_dead_tile[behavior]['error_a_means'].append(mean_angle_error)
            results_by_dead_tile[behavior]['error_d_std'].append(std_distance_error)
            results_by_dead_tile[behavior]['error_a_std'].append(std_angle_error)
            results_by_dead_tile[behavior]['error_sa_means'].append(mean_sangle_error)
            results_by_dead_tile[behavior]['error_sa_std'].append(std_sangle_error)

    plt.subplots(figsize=_colors.FIG_SIZE)
    pallette = _colors.create_palette(2)

    
    #DISTANCE ERROR
    for i, behavior in enumerate(results_by_dead_tile):
        dead_tiles = np.array(results_by_dead_tile[behavior]['dead_tiles'])
        error_d_means = np.array(results_by_dead_tile[behavior]['error_d_means'])
        error_d_std = np.array(results_by_dead_tile[behavior]['error_d_std'])

        #fill between
        plt.fill_between(dead_tiles, error_d_means - error_d_std, error_d_means + error_d_std, alpha=0.8, color=pallette[i])        
        plt.plot(dead_tiles, error_d_means, label=f'{_correct_behavior_name(behavior)}', color=pallette[i], alpha=1, zorder = 10)

    plt.legend()
    plt.xlabel('Dead Tiles [%]')
    plt.ylabel('Position Error [tiles]')
    ticks = [i/10 for i in range(10)]
    labels = [f'{int(t*100)}' for t in ticks]
    plt.xticks(ticks, labels)

    file_path = f'{_folders.VISUALIZATIONS_PATH}/dead_tile_error.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()

    #ANGLE ERROR
    for i, behavior in enumerate(results_by_dead_tile):
        dead_tiles = np.array(results_by_dead_tile[behavior]['dead_tiles'])
        error_a_means = np.array(results_by_dead_tile[behavior]['error_a_means'])
        error_a_std = np.array(results_by_dead_tile[behavior]['error_a_std'])
        error_sa_means = np.array(results_by_dead_tile[behavior]['error_sa_means'])
        error_sa_std = np.array(results_by_dead_tile[behavior]['error_sa_std'])

        #fill between
        plt.fill_between(dead_tiles, error_a_means - error_a_std, error_a_means + error_a_std, alpha=0.8, color=pallette[i])        
        plt.plot(dead_tiles, error_a_means, label=f'{_correct_behavior_name(behavior)}', color=pallette[i])

        #plt.fill_between(dead_tiles, error_sa_means - error_sa_std, error_sa_means + error_sa_std, alpha=0.3, color=pallette[i])
        #plt.plot(dead_tiles, error_sa_means, label=f'{behavior} Symmetry Free', color=pallette[i], linestyle='--')

    plt.legend()
    plt.xlabel('Dead Tiles [%]')
    plt.ylabel('Angle Error [$^\circ$]')
    ticks = [i/10 for i in range(10)]
    labels = [f'{int(t*100)}' for t in ticks]
    plt.xticks(ticks, labels)
    file_path = f'{_folders.VISUALIZATIONS_PATH}/dead_tile_angle_error.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    

if __name__ == '__main__':
    resultant_error()