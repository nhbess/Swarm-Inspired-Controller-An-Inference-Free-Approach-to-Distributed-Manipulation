import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from Tile import Tile
import pygame
import random
import numpy as np
from typing import Any


class Board:
    def __init__(self, N:int, TILE_SIZE:int):
        self.TILE_SIZE = TILE_SIZE
        self.X = N
        self.Y = N
        self.tiles: list[Tile] = self.create_tiles()
        self.create_neighbors()

    @property
    def net_vectors(self):
        sume = sum(np.array([tile.vector for tile in self.tiles]))
        return np.linalg.norm(sume)
    
    def update_knowledge(self):
        tiles = self.tiles.copy()
        random.shuffle(tiles)
        for tile in tiles:
            tile.update_knowledge()
    
    def reasoning(self):
        tiles = self.tiles.copy()
        random.shuffle(tiles)
        for tile in tiles:
            tile.reasoning()

    def act(self):
        tiles = self.tiles.copy()
        random.shuffle(tiles)
        for tile in tiles:
            if tile.is_alive:
                tile.update_knowledge()
                tile.execute_behavior()

    def execute_behavior(self):
        tiles = self.tiles.copy()
        random.shuffle(tiles)
        for tile in tiles:
            tile.execute_behavior()
    
    def create_tiles(self):
        tiles = []
        for y in range(self.Y):
            for x in range(self.X):
                tile = Tile()
                tile.x = x
                tile.y = y
                tile.rect = pygame.Rect(x*self.TILE_SIZE, y*self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                tile.mask = pygame.mask.from_surface(pygame.Surface((self.TILE_SIZE, self.TILE_SIZE)))
                tile.vector = np.array([0, 0], dtype=float)
                tile.id = len(tiles)
                tiles.append(tile)

                #Central pixel of the tile
                tile.center_rect = pygame.Rect(x*self.TILE_SIZE + self.TILE_SIZE//2, y*self.TILE_SIZE + self.TILE_SIZE//2, 1, 1)
                tile.center_mask = pygame.mask.from_surface(pygame.Surface((1, 1)))
  
                #Sensors
                n_sensor = 1
                padding = self.TILE_SIZE//6
                x_sensor = np.linspace(padding, self.TILE_SIZE-padding, n_sensor, dtype=int)
                y_sensor = np.linspace(padding, self.TILE_SIZE-padding, n_sensor, dtype=int)
                for xs in x_sensor:
                    for ys in y_sensor:
                        sx = x*self.TILE_SIZE + xs
                        sy = y*self.TILE_SIZE + ys
                        tile.sensors_centers.append(pygame.Rect(sx, sy, 1, 1))
                        #tile.sensors_centers.append(pygame.Rect(xs*self.TILE_SIZE, ys*self.TILE_SIZE, 1, 1))
                        tile.sensors_masks.append(pygame.mask.from_surface(pygame.Surface((1, 1))))
        return tiles

    def kill_tiles(self, ratio:float):
        tiles = self.tiles.copy()
        random.shuffle(tiles)

        to_kill = int(len(tiles) * ratio)
        while to_kill > 0:
            if len(tiles) == 0:
                break
            tile = tiles.pop()
            if tile.is_target:
                continue
            else:
                tile.die()
                to_kill -= 1
                
    def get_tile(self, x:int, y:int):
        if x < 0 or x >= self.X or y < 0 or y >= self.Y:
            return None
        return self.tiles[x + y*self.Y]
     
    def create_neighbors(self):
        for tile in self.tiles:
            x, y = tile.get_coordinates()
            neighbors = [(x, y+1), (x, y-1), (x-1, y), (x+1, y)]
            for nx, ny in neighbors:
                neighbor_tile = self.get_tile(nx, ny)
                if neighbor_tile:
                    tile.neighbors.append(neighbor_tile)
                        
    def vectors_to_center(self):
        for t in self.tiles:
            t.vector = np.array([self.X//2 - t.x, self.Y//2 - t.y], dtype=float)
    
    def vectors_to_right(self):
        for t in self.tiles:
            t.vector = np.array([1, 0], dtype=float)

    def vectors_to_none(self):
        for t in self.tiles:
            t.vector = np.array([0, 0], dtype=float)

    def vectors_to_random(self):
        for t in self.tiles:
            t.vector = np.array([random.randint(-5,5), random.randint(-5,5)], dtype=float)

    def draw(self, window):
        setup = {
            'draw_sensors': False,
            'target_color': (255, 0, 0),
        }
        
        for tile in self.tiles:
            if not tile.is_alive:
                continue

            #TODO: im not sure why this is needed
            if tile.is_target:
                tile.color = setup['target_color']
            
            pygame.draw.rect(window, tile.color, tile.rect, width=self.TILE_SIZE//10)
            
            vector = tile.vector

            col, row = tile.get_coordinates()
            tc = (col * self.TILE_SIZE + self.TILE_SIZE // 2, row * self.TILE_SIZE + self.TILE_SIZE // 2)
            th = self.TILE_SIZE
            tw = self.TILE_SIZE
            #pygame.draw.circle(self.window, (123,123,132), tc, self.TILE_SIZE//2, width=1)
            
            length = np.linalg.norm(vector)
            if length == 0:
                pygame.draw.circle(window, (123,123,132), tc, self.TILE_SIZE//10)
            else:
                vector = vector / length
                #pygame.draw.circle(self.window, (123,123,132), (tc[0] + vector[0] * tw//2, tc[1] + vector[1] * th//2), self.TILE_SIZE//10)
                color = (123,123,132)
                #random color
                #color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                pygame.draw.line(window, color, tc, (tc[0] + vector[0] * tw//2, tc[1] + vector[1] * th//2), width=3)
                pygame.draw.circle(window, color, tc, self.TILE_SIZE//10)
            
            if setup['draw_sensors']:
                for sensor in tile.sensors_centers:
                    pygame.draw.circle(window, (255, 255, 255), sensor.center, 1)

    def get_coverage(self):
        target_tiles = [tile for tile in self.tiles if tile.is_target]
        contacts = [tile for tile in target_tiles if tile.is_contact]
        #print(f'Contacts: {len(contacts)}, Target tiles: {len(target_tiles)}, Coverage: {len(contacts)/len(target_tiles)}')
        return len(contacts)/len(target_tiles)

    def get_system_data(self):
        data = {
        'contacts' : [tile.is_contact for tile in self.tiles],
        'vectors_translation' : [tile.vector_translation.tolist() for tile in self.tiles],
        'vectors_rotation' : [tile.vector_rotation.tolist() for tile in self.tiles],
        'vectors' : [tile.vector.tolist() for tile in self.tiles],
        'signals_A' : [tile.signal_center_excitation_A for tile in self.tiles],
        #'signals_B' : [tile.signal_center_excitation_B for tile in self.tiles],
        }
        return data

if __name__ == "__main__":
    print("Board.py")
    import sys
    random.seed(1)
    b = Board (3, 50)
    for k,v in b.board_info().items():
        print(k, v)
