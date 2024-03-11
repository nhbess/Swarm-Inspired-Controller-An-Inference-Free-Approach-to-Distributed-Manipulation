from Tile import Tile
from TunableParameters import TunableParameters

import numpy as np

class Behaviors:
    @staticmethod
    def information_diffusion(tile:Tile):
        if not tile.is_alive:
            return

        if tile.is_target:
            tile.vector = np.array([0, 0], dtype=float)
            tile.vector_translation = np.array([0, 0], dtype=float)
            tile.vector_rotation = np.array([0, 0], dtype=float)
            return
        
        target_neighbors = [neighbor for neighbor in tile.knowledge.keys() if tile.knowledge[neighbor]['is_target']]
        if target_neighbors:
        
            #point to the target
            x = sum(tile.knowledge[neighbor]['x'] for neighbor in target_neighbors) / len(target_neighbors)
            y = sum(tile.knowledge[neighbor]['y'] for neighbor in target_neighbors) / len(target_neighbors)
            avg_target_position = np.array([x, y], dtype=float)
            my_position = np.array([tile.x, tile.y], dtype=float)
            vector_to_object = avg_target_position - my_position
            
            if np.linalg.norm(vector_to_object) != 0:
                tile.vector_translation = vector_to_object / np.linalg.norm(vector_to_object)
                tile.vector = tile.vector_translation
            else:
                tile.vector_translation = np.array([0, 0], dtype=float)
                tile.vector = tile.vector_translation
            
        else:
            x = sum(tile.knowledge[neighbor]['vector_translation'][0] for neighbor in tile.knowledge.keys()) / len(tile.knowledge.keys())
            y = sum(tile.knowledge[neighbor]['vector_translation'][1] for neighbor in tile.knowledge.keys()) / len(tile.knowledge.keys())
            
            vector_translation = np.array([x, y], dtype=float)
            
            if np.linalg.norm(vector_translation) != 0:
                tile.vector_translation = vector_translation / np.linalg.norm(vector_translation)
                tile.vector = tile.vector_translation
            else:
                tile.vector_translation = np.array([0, 0], dtype=float)
                tile.vector = tile.vector_translation
                        
            
        #Add information about the target to the knowledge
        avg_target_center = np.array([0, 0], dtype=float)
        avg_target_angle = 0
        
        for neighbor in tile.knowledge.keys():
            avg_target_center += tile.knowledge[neighbor]['target_center']
            avg_target_angle += tile.knowledge[neighbor]['target_angle']
        
        avg_target_center = avg_target_center / len(tile.knowledge)
        avg_target_angle = avg_target_angle / len(tile.knowledge)
        
        tile.target_center = avg_target_center
        tile.target_angle = avg_target_angle
    
        if tile.is_contact:
            object_center = np.array(tile.object_center, dtype=float) + np.array([0.5, 0.5], dtype=float)
            tile_center = np.array([tile.x, tile.y], dtype=float) + np.array([0.5, 0.5], dtype=float)
            r =  tile_center - object_center
            
            perpendicular = np.array([-r[1], r[0]], dtype=float)
            if np.linalg.norm(perpendicular) != 0:
                perpendicular = perpendicular / np.linalg.norm(perpendicular)
            else:
                perpendicular = np.array([0, 0], dtype=float)
            
            error = tile.target_angle - tile.object_angle
            #print(f'final: {self.target_angle}, initial: {self.object_angle}, error: {error}')
            if error > 180:
                error = error - 360
            tile.vector_rotation =  2*(-error)/180*perpendicular
            
            tile.vector = tile.vector_translation + tile.vector_rotation
        else:
            tile.vector_rotation = np.array([0, 0], dtype=float)
            tile.vector = tile.vector_translation

    @staticmethod
    def behavior_swarmy_rotation(tile:Tile) -> None:
        TILE_SIZE = 1

        if tile.is_target:
            return

        #CALCUATE TRANSLATION
        if len(tile.target_neighbors)>0: #Membrane
            # CALCULATE EXCITATION SIGNAL
            s_val = tile.signal_center_excitation_A
            s_val = s_val * TunableParameters.shrink_x
            if tile.is_contact and not tile.is_target:
                s_val = s_val + TunableParameters.excitation_factor * (1.0 - TunableParameters.shrink_x)
            tile.signal_center_excitation_A = s_val

            avg_target_neighbors = np.mean([neighbor.center for neighbor in tile.target_neighbors], axis=0)
            tile.vector_translation = avg_target_neighbors - tile.center

            if tile.signal_center_excitation_A > TunableParameters.threshold_x_a:

                if tile.vector_translation[0] == 0:
                    if tile.vector_translation[1] > 0:
                        tile.vector_translation[0] = TILE_SIZE
                        tile.vector_translation[1] = TILE_SIZE
                    elif tile.vector_translation[1] < 0:
                        tile.vector_translation[0] = -TILE_SIZE
                        tile.vector_translation[1] = -TILE_SIZE
                else:
                    if tile.vector_translation[0] > 0:
                        tile.vector_translation[0] = TILE_SIZE
                        tile.vector_translation[1] = -TILE_SIZE
                    elif tile.vector_translation[0] < 0:
                        tile.vector_translation[0] = -TILE_SIZE
                        tile.vector_translation[1] = TILE_SIZE

        else:
            tile.vector_translation = np.mean([neighbor.vector_translation for neighbor in tile.neighbors], axis=0)

        if np.linalg.norm(tile.vector_translation) > 0:
            tile.vector_translation = tile.vector_translation / np.linalg.norm(tile.vector_translation)

        tile.vector = tile.vector_translation #+ tile.vector_rotation