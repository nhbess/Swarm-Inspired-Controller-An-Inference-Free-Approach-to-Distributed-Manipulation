import json
import os

import matplotlib.pyplot as plt
import numpy as np

import _colors
import _folders
import gzip
import sys

experiment_name=f'_Comparison'
_folders.set_experiment_folders(experiment_name)
import _config

def _correct_behavior_name(behavior):
    if behavior == 'Information Diffusion':
        return behavior
    if behavior == 'Swarmy':
        return 'Swarm Inspired'
    
    raise ValueError(f'Behavior {behavior} not recognized')
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
    def get_convergence_step(arr):
        if len(arr) <= 1: return 0
        last_value = arr[-1]
        for index, value in enumerate(reversed(arr)):
            if value != last_value: return len(arr) - index
        return len(arr)

    for behavior in exp_data:
        data_behavior = exp_data[behavior]
        target_centers = np.array([run['TARGET_CENTER'] for run in data_behavior])
        target_angles = np.array([run['TARGET_ANGLE'] for run in data_behavior])
        tile_sizes = np.array([run['TILE_SIZE'] for run in data_behavior])
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
        

        #Convergence and Coverage
        final_coverage = np.array([run['coverage'][-1] for run in data_behavior])
        time_to_convergence = np.array([get_convergence_step(run['coverage']) for run in data_behavior])


        shapes_errors = {}
        for i, shape in enumerate(shapes):
            if shape not in shapes_errors:
                shapes_errors[shape] = {'distance_error': [], 'angle_error': []}
            shapes_errors[shape]['distance_error'].append(resultant_distance_error[i])
            shapes_errors[shape]['angle_error'].append(resultant_angle_error[i])


        results[behavior] = {
            'distance_error': resultant_distance_error,
            'angle_error': resultant_angle_error,
            'coverage': final_coverage,
            'time_to_convergence': time_to_convergence,
            'shapes_errors': shapes_errors,
            'symmetry_free_angle_error': symmetry_free_angle_error
        }
    return results


def resultant_error():
    results = _get_results()
    
    plt.subplots(figsize=_colors.FIG_SIZE)
    pallette = _colors.create_palette(2)
    
    #DISTANCE ERROR
    max_value = max(np.max(results[behavior]['distance_error']) for behavior in results)
    min_value = min(np.min(results[behavior]['distance_error']) for behavior in results)

    n_bins = 17
    bins = np.linspace(min_value, max_value, n_bins)

    for i, behavior in enumerate(results):
        distance_error = results[behavior]['distance_error']
        mean = np.mean(distance_error)
        std = np.std(distance_error)
        plt.hist(distance_error, bins=bins, alpha=0.6, label=f'{_correct_behavior_name(behavior)}', facecolor=pallette[i], weights=100*np.ones_like(distance_error) / len(distance_error))
        plt.axvline(mean, color=pallette[i],  linewidth=1, label=f'$\mu:{mean:.2f}$,  $\sigma:{std:.2f}$', alpha=0.6)
    

    plt.legend()
    plt.xlabel('Position Error [tiles]')
    plt.ylabel('Frequency [%]')    
    file_path = f'{_folders.VISUALIZATIONS_PATH}/distance_error.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()

    #ANGLE ERROR
    max_value = max(np.max(results[behavior]['angle_error']) for behavior in results)
    min_value = min(np.min(results[behavior]['angle_error']) for behavior in results)

    n_bins = 20
    bins = np.linspace(min_value, max_value, n_bins)

    for i, behavior in enumerate(results):
        sf_angle_error = results[behavior]['angle_error']
        mean = np.mean(sf_angle_error)
        std = np.std(sf_angle_error)
        plt.hist(sf_angle_error, bins=bins, alpha=0.6, label=f'{_correct_behavior_name(behavior)}', facecolor=pallette[i], weights=100*np.ones_like(sf_angle_error) / len(sf_angle_error))
        plt.axvline(mean, color=pallette[i],  linewidth=1, label=f'$\mu:{mean:.2f}$,  $\sigma:{std:.2f}$', alpha=0.6)

    plt.legend()
    plt.xlabel('Angle Error [$^\circ$]')
    plt.ylabel('Frequency [%]')    
    #y log scale
    #plt.yscale('log')
    file_path = f'{_folders.VISUALIZATIONS_PATH}/angle_error.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()


    #SYMETTRY FREE ANGLE ERROR
    max_value = max(np.max(results[behavior]['symmetry_free_angle_error']) for behavior in results)
    min_value = min(np.min(results[behavior]['symmetry_free_angle_error']) for behavior in results)

    n_bins = 20
    bins = np.linspace(min_value, max_value, n_bins)

    for i, behavior in enumerate(results):
        sf_angle_error = results[behavior]['symmetry_free_angle_error']
        mean = np.mean(sf_angle_error)
        std = np.std(sf_angle_error)
        plt.hist(sf_angle_error, bins=bins, alpha=0.6, label=f'{_correct_behavior_name(behavior)}', facecolor=pallette[i], weights=100*np.ones_like(sf_angle_error) / len(sf_angle_error))
        plt.axvline(mean, color=pallette[i],  linewidth=1, label=f'$\mu:{mean:.2f}$,  $\sigma:{std:.2f}$', alpha=0.6)

    plt.legend()
    plt.xlabel('Angle Error Symmetry Free[$^\circ$]')
    plt.ylabel('Frequency [%]')    
    #y log scale
    #plt.yscale('log')
    file_path = f'{_folders.VISUALIZATIONS_PATH}/sf_angle_error.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()


    #COVERAGE
    max_value = max(np.max(results[behavior]['coverage']) for behavior in results)
    min_value = min(np.min(results[behavior]['coverage']) for behavior in results)

    n_bins = 10
    bins = np.linspace(min_value, max_value, n_bins)

    for i, behavior in enumerate(results):
        time_to_convergence = results[behavior]['coverage']
        mean = np.mean(time_to_convergence)
        std = np.std(time_to_convergence)
        plt.hist(time_to_convergence, bins=bins, alpha=0.6, label=f'{_correct_behavior_name(behavior)}', facecolor=pallette[i], weights=100*np.ones_like(time_to_convergence) / len(time_to_convergence))
        plt.axvline(mean, color=pallette[i],  linewidth=1, label=f'$\mu:{mean:.2f}$,  $\sigma:{std:.2f}$', alpha=0.6)

    plt.legend()
    plt.xlabel('Coverage [%]')
    plt.ylabel('Frequency [%]')    
    file_path = f'{_folders.VISUALIZATIONS_PATH}/coverage.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()
    
    #TIME
    max_value = max(np.max(results[behavior]['time_to_convergence']) for behavior in results)
    min_value = min(np.min(results[behavior]['time_to_convergence']) for behavior in results)

    n_bins = 15
    bins = np.linspace(min_value, max_value, n_bins)

    for i, behavior in enumerate(results):
        time_to_convergence = results[behavior]['time_to_convergence']
        mean = np.mean(time_to_convergence)
        std = np.std(time_to_convergence)
        plt.hist(time_to_convergence, bins=bins, alpha=0.6, label=f'{_correct_behavior_name(behavior)}', facecolor=pallette[i], weights=100*np.ones_like(time_to_convergence) / len(time_to_convergence))
        plt.axvline(mean, color=pallette[i],  linewidth=1, label=f'$\mu:{mean:.2f}$,  $\sigma:{std:.2f}$', alpha=0.6)

    plt.legend()
    plt.xlabel('Operation Period [update steps]')
    plt.ylabel('Frequency [%]')    
    file_path = f'{_folders.VISUALIZATIONS_PATH}/operation_period.png'
    plt.savefig(file_path, bbox_inches='tight', dpi=600)
    #plt.show()
    plt.clf()
    

if __name__ == '__main__':
    resultant_error()
