import os
import pandas as pd
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from Board import Board
from Tile import Tile
from Tetromino import Tetromino
import pygame
import sys
import numpy as np
import random
import time
from collections import deque
import imageio
from DataHandler import DH

class Simulator:
    def __init__(self, setup:dict):
        self.pause = False
        self.setup = setup
        self.board = Board(self.setup['N'], self.setup['TILE_SIZE'])        

        #End condition variables
        self.memory_length = 100
        self.error_position = deque(maxlen=self.memory_length)
        self.error_angle = deque(maxlen=self.memory_length)

        #Data variables
        if self.setup['save_data']:
            self.dh = DH()
            self.dh.add_data( 
                BOARD_SIZE = self.setup['N'],
                TILE_SIZE = self.setup['TILE_SIZE'],
                SHAPE = self.setup['symbol'],
                RESOLUTION = self.setup['resolution'],
                DEAD_TILES = self.setup['dead_tiles'])


        if self.setup['visualize']: 
            pygame.init()
            self.clock = pygame.time.Clock()
            pygame.font.init()
            pygame.display.set_caption('SimuV1')

        if self.setup['object']:
            self.tetromino = Tetromino(self.setup['symbol'], self.setup['TILE_SIZE'], resolution=self.setup['resolution'])
            #self.tetromino.rect.center = (self.board.X*self.board.TILE_SIZE//2, self.board.Y*self.board.TILE_SIZE//2)       
            #self.tetromino.rect.center = (0, 0)
            self.tetromino.rect.center = (random.randint(0, self.setup['N']*self.board.TILE_SIZE),random.randint(0, self.setup['N']*self.board.TILE_SIZE))
            self.tetromino.rotate(random.randint(-180, 180), allow_max_rotation=False)
            
        for _ in range(self.setup['n_random_targets']):
            self.board.get_tile(random.randint(0, self.board.X-1), random.randint(0, self.board.Y-1)).set_as_target()

        if self.setup['target_shape']:
            self.target = Tetromino(self.setup['symbol'], self.setup['TILE_SIZE'], resolution=self.setup['resolution'])
            
            #Random target
            self.target.set_angle(random.randint(-180, 180))
            self.target.rect.center = (self.board.X*self.board.TILE_SIZE//2, self.board.Y*self.board.TILE_SIZE//2 + 25)
            
            #Fixed target
            #self.target.set_angle(90)
            #self.target.rect.center = (self.board.X*(self.board.TILE_SIZE -5), self.board.Y*(self.board.TILE_SIZE -10))
            
            self.target.center = self.target.get_geometric_center()
            self.set_target_shape_tiles()
            if self.setup['save_data']:
                self.dh.add_data(TARGET_CENTER = self.target.center.tolist(), 
                                 TARGET_ANGLE = self.target.angle%360,
                                 TARGET_TILES = [tile.is_target for tile in self.board.tiles],
                                 TARGET_POLYGON = self.target.mask.outline())
        #Setting the window
        if self.setup['visualize']:
            self.window = pygame.display.set_mode((self.board.X*self.board.TILE_SIZE, self.board.Y*self.board.TILE_SIZE))

        self.border_rect = pygame.Rect(0, 0, self.board.X*self.board.TILE_SIZE, self.board.Y*self.board.TILE_SIZE)
        if self.setup['object']: self.tetromino.rect.clamp_ip(self.border_rect)
        if self.setup['target_shape']: self.target.rect.clamp_ip(self.border_rect)
        if self.setup['dead_tiles']: self.board.kill_tiles(self.setup['dead_tiles'])

        self.board.vectors_to_none()

    def set_target_shape_tiles(self) -> None:
        '''
        Set the tiles that are in contact with the target surface as target tiles.
        It also set the angle and the center of the target surface into the knowledge of the tiles.
        '''
        for tile in self.board.tiles:
            offset_x = - self.target.rect.x + tile.center_rect.left
            offset_y = - self.target.rect.y + tile.center_rect.top
            offset = (offset_x, offset_y)
            offset = (offset_x, offset_y)

            if self.target.mask.overlap(tile.center_mask, offset) != None:
                tile.set_as_target()
                tile.target_angle = self.target.angle
                tile.target_center = self.target.rect.center
             
    def get_and_set_contact_tiles(self)->list[Tile]:
        contact_tiles = []
        for tile in self.board.tiles:
            if not tile.is_alive: continue
            offset_x = - self.tetromino.rect.x + tile.center_rect.left
            offset_y = - self.tetromino.rect.y + tile.center_rect.top
            offset = (offset_x, offset_y)
            offset = (offset_x, offset_y)
            if self.tetromino.mask.overlap(tile.center_mask, offset) != None:
                tile.set_as_contact()
                contact_tiles.append(tile)
            else:
                tile.set_as_no_contact()
        return contact_tiles

    def calculate_displacement(self, contact_tiles:list[Tile]) -> np.array:
        resultant_vector = np.array([0, 0], dtype=float)
        for tile in contact_tiles:
            resultant_vector += tile.vector
            
        length = np.linalg.norm(resultant_vector)
        if length != 0:
            return resultant_vector / length
        else:
            return np.array([0, 0])

    def calculate_rotation(self, contact_tiles:list[Tile]) -> float:
        rotation = 0
        tetromino_center = np.array(self.tetromino.rect.center)

        for tile in contact_tiles:
            tile_center = np.array(tile.rect.center)
            
            vector_tetromino_tile = -tile_center + tetromino_center
            length = np.linalg.norm(vector_tetromino_tile)
            if length == 0:
                continue
            r = vector_tetromino_tile / length
            f = tile.vector
            rotation += np.cross(r, f)
        return rotation  

    def run_simulation(self, save_sys_data = False):
        self.begin_time = time.time()
        previous_time = time.time()
        if self.setup['save_animation']: self.frames = []
        iterations = 0
        while True:
            if not self.pause:
                #self.board.get_coverage()
                if self.setup['save_data']:
                    #data_system = self.board.board_info()
                    #data_system['object_center'] = self.tetromino.center.tolist()
                    #data_system['object_angle'] = self.tetromino.angle
                    self.dh.add_data(object_center_x = self.tetromino.center.tolist()[0],
                                     object_center_y = self.tetromino.center.tolist()[1],
                                     object_angle = self.tetromino.angle%360,
                                     coverage = self.board.get_coverage())
                    if save_sys_data:
                        sys_data = self.board.get_system_data()
                        self.dh.add_data_list(**sys_data)
                        tetro_polygon = self.tetromino.mask.outline()
                        tetro_polygon = [list(point) for point in tetro_polygon]
                        self.dh.add_data_list(TETROMINO_POLYGON = tetro_polygon)


            if self.setup['visualize']:
                self.window.fill(0)
                self.handle_keyboard_input()
        
            # Action of the agent
            if not self.pause:
                
                self.board.act()

                if self.setup['object']: self.tetromino.rect.clamp_ip(self.border_rect)
                if self.setup['object']: contact_tiles = self.get_and_set_contact_tiles()        

                if self.setup['object']:# and time.time() - previous_time > 3: 
                    self.fill_missing_information(contact_tiles)
                    resultant_vector = self.calculate_displacement(contact_tiles)
                    rotation = self.calculate_rotation(contact_tiles)
           
                    self.tetromino.move(resultant_vector)
                    self.tetromino.rotate(rotation)
    
                if self.setup['visualize']: self.board.draw(self.window)
                if self.setup['delay']: time.sleep(0.5)
                if self.setup['show_tetromines'] and self.setup['visualize'] and self.setup['object']:
                    self.tetromino.draw(self.window)
                
                if self.setup['show_tetromino_contour'] and self.setup['visualize'] and self.setup['object']:
                    self.tetromino.draw_contour(self.window)
                    if self.setup['target_shape']:
                        self.target.draw_contour(self.window)
                
                
                if self.setup['visualize']:
                    pygame.display.update()
                    #self.clock.tick(60)
                    if self.setup['save_animation']:
                        frame = pygame.surfarray.array3d(self.window)
                        self.frames.append(frame)

                '''
                if iterations > self.setup['max_iterations']:
                    if self.setup['save_data']: return self.dh.data
                    break
                iterations += 1
                '''
                # End condition
                
                if self.setup['object'] and True:
                    err_pos = np.linalg.norm(np.array(self.tetromino.rect.center) - np.array(self.target.rect.center))
                    err_ang = abs(self.tetromino.angle - self.target.angle)
                    self.error_position.append(err_pos)
                    self.error_angle.append(err_ang)

                    if len(self.error_position) == self.memory_length:
                        first_half_pos = [self.error_position[i] for i in range(self.memory_length//2)]
                        second_half_pos = [self.error_position[i] for i in range(self.memory_length//2, self.memory_length)]
                        avg_1_pos = sum(first_half_pos)/len(first_half_pos)
                        avg_2_pos = sum(second_half_pos)/len(second_half_pos)
                        if avg_1_pos == 0 and avg_2_pos == 0:
                            diff_pos = 0
                        else:
                            diff_pos =  abs(avg_1_pos - avg_2_pos) / ((avg_1_pos + avg_2_pos) / 2) * 100

                        first_half_ang = [self.error_angle[i] for i in range(self.memory_length//2)]
                        second_half_ang = [self.error_angle[i] for i in range(self.memory_length//2, self.memory_length)]
                        avg_1_ang = sum(first_half_ang)/len(first_half_ang)
                        avg_2_ang = sum(second_half_ang)/len(second_half_ang)
                        if avg_1_ang == 0 and avg_2_ang == 0:
                            diff_ang = 0
                        else:
                            diff_ang =  abs(avg_1_ang - avg_2_ang) / ((avg_1_ang + avg_2_ang) / 2) * 100
                        #print("diff_pos: ", diff_pos, "diff_ang: ", diff_ang)

                        min_diff = 5
                        if diff_pos < min_diff and diff_ang < min_diff:
                            #print("Success! approximate")
                            if self.setup['save_data']: return self.dh.data
                            if self.setup['save_animation']:
                                name = self.setup['save_animation']
                                imageio.mimsave(f'{name}.gif', self.frames, duration=20)
                            break
                
                if self.setup['shuffle_targets']:
                    if time.time() - previous_time > 3:
                        self.shuffle_targets()
                        previous_time = time.time()
                
                iterations += 1
                if iterations > self.setup['max_iterations']:
                    return self.dh.data
                    
    def fill_missing_information(self, contact_tiles: list[Tile]) -> None: #Temporary hack
        '''
        This is an external source of information to cover the missing skill from the side of the tiles
        to identify the object that is in contact with them.
        Both target and tetromino angles and positions need to be known to the tiles.
        '''
        for tile in contact_tiles:
                center = self.tetromino.rect.center
                center = (center[0]//self.board.TILE_SIZE, center[1]//self.board.TILE_SIZE)
                tile.object_angle = self.tetromino.angle
                tile.object_center = center
                
    def shuffle_targets(self):
        for tile in self.board.tiles:
            if tile.is_target:
                while True:
                    new_tile = self.board.get_tile(random.randint(0, self.board.X-1), random.randint(0, self.board.Y-1))
                    if not new_tile.is_target:
                        new_tile.set_as_target()
                        tile.set_as_no_target()
                        break
              
    def handle_keyboard_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause = not self.pause
                    if self.pause:
                        pygame.display.set_caption("Pause")
                    else:
                        pygame.display.set_caption("Tetris")

            if event.type == pygame.QUIT:
                if self.setup['save_data']:
                    self.save_data()
                if self.setup['save_animation']:
                    name = self.setup['save_animation']
                    imageio.mimsave(f'{name}.gif', self.frames, fps=30)
                
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.setup['save_data']:
                        self.save_data()
                    if self.setup['save_animation']:
                        name = self.setup['save_animation']
                        imageio.mimsave(f'{name}.gif', self.frames, fps=30)
                    pygame.quit()
                    sys.exit()

    def save_data(self):
        filename = self.setup['file_name']
        self.dh.save_json(filename)
        print(f"    Data {filename} saved.")

if __name__ == "__main__":
    pass