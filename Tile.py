import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
from typing import Any

class Tile:
    def __init__(self) -> None:
        
        self.id:int = None
        self.is_alive:bool = True

        self.rect: pygame.Rect = None
        self.mask: pygame.mask = None
        self.original_color = (50, 50, 50)
        self.color = self.original_color

        self.center_rect: pygame.Rect = None
        self.center_mask: pygame.mask = None
        self.mask_color = (255, 0, 0)

        self.sensors_centers = []
        self.sensors_masks = []     


        # Knowledge:
        self.neighbors:list[Tile] = []
        
        self.vector = np.array([0, 0], dtype=float)     # Shared
        self.vector_translation = np.array([0, 0], dtype=float)
        self.vector_rotation = np.array([0, 0], dtype=float)
        
        self.x: int = None                              # Shared
        self.y: int = None                              # Shared                  
        self.is_target:bool = False                     # Shared
        self.is_contact:bool = False                    # Shared
        
        self.object_center = np.array([0, 0], dtype=float)
        self.object_angle: float = 0
        
        self.target_center = np.array([0, 0], dtype=float)             
        self.target_angle: float = 0                 

        self.knowledge:dict[Tile, dict[str, Any]] = {}

        # Signals:
        self.signal_center_excitation_A = 0
        
    @property
    def target_neighbors(self):
        return [neighbor for neighbor in self.neighbors if neighbor.is_target]
    
    @property
    def center(self):
        return np.array([self.x, self.y], dtype=float)
    
    @property
    def number_of_neighbors(self):
        if not self.is_alive:
            return None        
        alive_neighbors = [neighbor for neighbor in self.neighbors if neighbor.is_alive]
        return len(alive_neighbors)
    
    
    def get_dict(self):
        return {
            'id': self.id,
            'position': [self.x,self.y],
            'is_target': self.is_target,
            'is_contact': self.is_contact,
            'is_alive': self.is_alive,
            'number_of_neighbors': self.number_of_neighbors(),
            
            'object_center': [self.object_center[0], self.object_center[1]],
            'object_angle': self.object_angle,
            'target_center': [self.target_center[0],self.target_center[1]],
        
            'target_angle': self.target_angle,
            'vector': self.vector.tolist(),
            'vector_translation': self.vector_translation.tolist(),
            'vector_rotation': self.vector_rotation.tolist(),
            'signal_A': self.signal_center_excitation_A,
            #'signal_B': self.signal_center_excitation_B,
        }
    
    def update_knowledge(self):
        if not self.is_alive:
            return
        for neighbor in self.neighbors:
            self.knowledge[neighbor] = {}
            self.knowledge[neighbor]['x'] = neighbor.x  #this is not going to change
            self.knowledge[neighbor]['y'] = neighbor.y  #this is not going to change

            self.knowledge[neighbor]['vector'] = neighbor.vector
            self.knowledge[neighbor]['vector_translation'] = neighbor.vector_translation
            self.knowledge[neighbor]['vector_rotation'] = neighbor.vector_rotation

            self.knowledge[neighbor]['is_target'] = neighbor.is_target
            self.knowledge[neighbor]['is_contact'] = neighbor.is_contact

            self.knowledge[neighbor]['object_center'] = neighbor.object_center
            self.knowledge[neighbor]['object_angle'] = neighbor.object_angle 

            self.knowledge[neighbor]['target_center'] = neighbor.target_center
            self.knowledge[neighbor]['target_angle'] = neighbor.target_angle


    def execute_behavior(self):
        raise NotImplementedError

    def die(self):
        self.is_alive = False
        self.color = (0,0,0)
        self.vector = np.array([0, 0], dtype=float)
        self.vector_translation = np.array([0, 0], dtype=float)
        self.vector_rotation = np.array([0, 0], dtype=float)

        for neighbor in self.knowledge.keys():
            neighbor.knowledge.pop(self)


    #GETTERS, SETTERS AND PRINTERS

    def set_as_target(self):
        self.is_target = True
        self.color = (255,0,0)

    def set_as_no_target(self):
        self.is_target = False
        self.color = self.original_color

    def set_as_contact(self):
        self.is_contact = True
        self.color = (255,160,122)
    
    def set_as_no_contact(self):
        self.is_contact = False
        self.color = self.original_color

    def get_coordinates(self):
        return (self.x, self.y)

    def print_details(self, show_knowledge:bool = False):
        print(f"Tile {self.id}")
        print(f"Position: ({self.x}, {self.y})")
        print(f"Vector: {self.vector}")
        print(f"Vector translation: {self.vector_translation}")
        print(f"Vector rotation: {self.vector_rotation}")
        print(f"Is target: {self.is_target}")
        print(f"Is contact: {self.is_contact}")
        print(f"Object angle: {self.object_angle}")
        print(f"Object center: {self.object_center}")

        print(f"Target angle: {self.target_angle}")
        print(f"Target center: {self.target_center}")
        print(f"Neighbors: {[neighbor.id for neighbor in self.neighbors]}")
        if show_knowledge:
            print(f"Knowledge:")#{self.knolwedge}")
            for key, value in self.knowledge.items():
                print(f"|    Tile {key.id}")
                for k, v in value.items():
                    print(f"|        | {k}: {v}")
        print()
    
    def __repr__(self) -> str:
        return f"Tile {self.id}"
    
    def __str__(self) -> str:
        return f"Tile {self.id}"

if __name__ == '__main__':
    pass
