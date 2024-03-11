import ast
import glob
import math
import os
import sys

import matplotlib.cm as cm
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import shapely.affinity
import shapely.plotting
from matplotlib.patches import Arc, Circle, Wedge
from shapely.geometry import Point, Polygon
import json

class COLORS:
    import _colors
    palette = _colors.create_palette(4,normalize=True)

    OBJECT =        palette[1]
    TARGET =        palette[3]
    CONTACT_TILE =  palette[0]
    TARGET_TILE =   palette[0]
    GRID =          '#d3d3d3'
    FONT_SIZE = 12

tetros_dict = {
'L' : np.array([(0, 0), (0, 3), (1, 3), (1, 1), (2, 1), (2, 0)]),
'O' : np.array([(0, 0), (0, 2), (2, 2), (2, 0)]),
'T' : np.array([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 1), (3, 1), (3, 0)]),
'I' : np.array([(0, 0), (0, 1), (4, 1), (4, 0)]),
'S' : np.array([(0, 0), (0, 1), (1, 1), (1, 2), (3, 2), (3, 1), (2, 1), (2, 0)]),
'Z' : np.array([(0, 2), (2, 2), (2, 1), (3, 1), (3, 0), (1, 0), (1, 1), (0, 1)]),
'J' : np.array([(0, 0), (0, 1), (1, 1), (1, 3), (2, 3), (2, 0)]),
}

class Tetromino:
    def __init__(self, constructor_vertices:list[tuple], scaler:float = 1, color = 'b') -> None:
        self.__constructor_vertices = constructor_vertices*scaler
        self.id = id
        self.scaler = scaler
        self.polygon = Polygon(self.__constructor_vertices)
        self.color = color
        self.__angle = 0.0

    @property
    def center(self) -> tuple:
        center = self.polygon.centroid.coords.xy
        return np.array([center[0][0], center[1][0]])
    
    @property
    def vertices(self) -> np.array:
        vertices = self.polygon.exterior.coords.xy
        return np.array([vertices[0], vertices[1]]).T
    @property
    def constructor_vertices(self) -> np.array:
        return self.__constructor_vertices.tolist()
    @center.setter
    def center(self, new_center: tuple) -> None:
        self.polygon = shapely.affinity.translate(self.polygon, xoff=new_center[0] - self.center[0], yoff=new_center[1] - self.center[1], zoff=0.0)

    def rotate(self, angle: float) -> None:
        self.polygon = shapely.affinity.rotate(self.polygon, angle, origin='centroid', use_radians=False)
        self.__angle = (self.__angle + angle)%360

    def translate(self, direction) -> None:
        self.polygon = shapely.affinity.translate(self.polygon, xoff=direction[0], yoff=direction[1], zoff=0.0)
        

    def plot(self, plot=None, text=None, dtx=0, dty=0, hide_angle=False) -> None:
        '''
        It works with plt.plot but not for ax.plot
        '''
        # contour
        points = self.polygon.exterior.coords
        x_values, y_values = zip(*points)

        shapely.plotting.plot_polygon(self.polygon,
                                      add_points=False, 
                                      facecolor=self.color, 
                                      #edgecolor='black', 
                                      alpha=0.9, 
                                      zorder=3, 
                                      linewidth=0,
                                      )

    
        # center
        center = self.polygon.centroid
        plot.plot(center.x, center.y, 'o', color='black', zorder=3)
        radius = 0.5

        if not hide_angle:
            # plot angle
            xangle = np.cos(np.deg2rad(self.angle))*radius*2
            yangle = np.sin(np.deg2rad(self.angle))*radius*2
            # print(xangle, yangle)
            plot.plot([center.x, center.x + xangle], [center.y,
                       center.y+yangle], color='black', zorder=3)
            plot.plot([center.x, center.x+radius*2],
                       [center.y, center.y], color='black', zorder=3)

            # plot arch
            ang = self.angle
            if ang > 0:
                arc = Arc((center.x, center.y), radius*2, radius*2,
                          theta1=0, theta2=ang, color='black', zorder=3)
            else:
                arc = Arc((center.x, center.y), radius*2, radius*2,
                          theta1=ang, theta2=0, color='black', zorder=3)

            # plt text if needed
            if text:
                # plot text between center and angle
                xtext = np.cos(np.deg2rad(self.angle/2))*radius/2
                ytext = np.sin(np.deg2rad(self.angle/2))*radius/2
                plot.text(center.x + xtext + dtx, center.y + ytext + dty,
                           text, color='black', zorder=4, fontsize=COLORS.FONT_SIZE)


            plot.gca().add_patch(arc)


            
    @property
    def angle(self) -> float:
        return self.__angle
    
    @angle.setter
    def angle(self, new_angle: float) -> None:
        angle = new_angle - self.__angle
        self.polygon = shapely.affinity.rotate(self.polygon, angle, origin='centroid', use_radians=False)
        self.__angle = new_angle

    
    def print_info(self) -> None:
        print('center: {}'.format(self.center))
        print('angle: {}'.format(self.__angle))

def contact_tiles(obj: Polygon, N: int, scaler=1, color='black', linestyle='-'):
    for i in range(N):
        for j in range(N):
            x = i*scaler
            y = j*scaler
            # if the object touchs the center of the tile
            if obj.contains(Point(i+0.5, j+0.5)):
                tile = Polygon([(i, j), (i+1, j), (i+1, j+1), (i, j+1)])
                shapely.plotting.plot_polygon(tile, 
                 add_points=False, 
                 facecolor='none',  # Set facecolor to 'none'
                 edgecolor=color,  # Specify the desired edgecolor
                 alpha=1,
                 zorder=2, 
                 linewidth=2,
                 linestyle=linestyle,
                 )
                
def membrane_tiles(obj: Polygon, N: int, scaler=1, color='black', linestyle='-'):
    
    grid = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            # if the object touchs the center of the tile
            if obj.contains(Point(i+0.5, j+0.5)):
                grid[j, i] = 1


    for i in range(N):
        for j in range(N):
            if grid[j, i] != 1:
                up = grid[j-1, i] if j > 0 else 0
                down = grid[j+1, i] if j < N-1 else 0
                left = grid[j, i-1] if i > 0 else 0
                right = grid[j, i+1] if i < N-1 else 0

                if up + down + left + right > 0:
                    tile = Polygon([(i, j), (i+1, j), (i+1, j+1), (i, j+1)])
                    shapely.plotting.plot_polygon(tile, 
                     add_points=False, 
                     facecolor='none',  # Set facecolor to 'none'
                     edgecolor=color,  # Specify the desired edgecolor
                     alpha=1,
                     zorder=2, 
                     linewidth=2,
                     linestyle=linestyle,
                     )
                                    
    #print(grid)
    #sys.exit()
#                tile = Polygon([(i, j), (i+1, j), (i+1, j+1), (i, j+1)])
#                shapely.plotting.plot_polygon(tile, 
#                 add_points=False, 
#                 facecolor='none',  # Set facecolor to 'none'
#                 edgecolor=color,  # Specify the desired edgecolor
#                 alpha=1,
#                 zorder=2, 
#                 linewidth=2,
#                 linestyle=linestyle,
#                 )

def contact_tiles_subfigures(ax, obj: Polygon, N: int, scaler=1, color='black', linestyle='-'):
    for i in range(N):
        for j in range(N):
            if obj.contains(Point(i+0.5, j+0.5)):
                tile_coords = [(i, j), (i+1, j), (i+1, j+1), (i, j+1)]
                tile = Polygon(tile_coords)
        
                points = tile.exterior.coords
                x_values, y_values = zip(*points)
                #ax.fill(x_values, y_values, color=color, alpha=0.9, zorder=2)
                ax.plot(x_values, y_values, color=color, linestyle=linestyle, linewidth=2, zorder=2)

def draw_tetro(tetrom, ax):
    '''
    The function plots the tetromino in the given axis
    '''
    points = tetrom.polygon.exterior.coords
    polygon = Polygon(points)
    simplified_polygon = polygon.simplify(0.1, preserve_topology=False)

    # Extract the simplified coordinates
    simplified_points = list(simplified_polygon.exterior.coords)
    x_values, y_values = zip(*simplified_points)
    
    
    ax.fill(x_values, y_values, color=tetrom.color, alpha=0.9, zorder=3)
    center = tetrom.polygon.centroid
    ax.plot(center.x, center.y, 'o', color='black', zorder=3)

def figure_environment():
    N = 9
    M = 8
    plt.figure(figsize=(3.5, 3.5))
    for i in range(N):
        for j in range(M):
            plt.plot([i, i+1], [j, j], COLORS.GRID)
            plt.plot([i, i], [j, j+1], COLORS.GRID)
            plt.plot([i, i+1], [j+1, j+1], COLORS.GRID)
            plt.plot([i+1, i+1], [j, j+1], COLORS.GRID)
            plt.plot(i+0.5, j+0.5, 'x', color=COLORS.GRID)

    resolution = 1.5

    symbol = 'J'
    vertex = tetros_dict[symbol]
    tetrom = Tetromino(vertex, resolution, COLORS.OBJECT)
    tetrom.rotate(100)
    tetrom.translate([1.15, 0.15])
    tetrom.plot(plot=plt, text='$\\alpha$', dtx=0.3, dty=0.15)
    
    
    target = Tetromino(vertex, resolution, COLORS.TARGET)
    target.rotate(200)
    target.translate([N*0.5, M*0.35])
    target.plot(plot=plt, text='$\\beta$', dtx=0.25, dty=0.25)
    
    contact_tiles(tetrom.polygon, N, COLORS.CONTACT_TILE, linestyle='--')
    membrane_tiles(target.polygon, N, COLORS.CONTACT_TILE, linestyle='dotted')
    contact_tiles(target.polygon, N, COLORS.TARGET_TILE, linestyle='-')



    plt.plot([], [], 's', label="Object", color=COLORS.OBJECT)
    plt.plot([], [], 's', label="Target placement", color=COLORS.TARGET)
    #plt.plot([], [], 's', label="Membrane tiles", color='lightgrey')
    plt.plot([], [], '--', label="Contact tiles", color=COLORS.CONTACT_TILE)
    plt.plot([], [], '-', label="Target tiles", color=COLORS.TARGET_TILE)
    plt.plot([], [], ':', label="Membrane tiles", color=COLORS.TARGET_TILE)
    plt.plot([], [], 'x', label="Sensor", color=COLORS.GRID)
    plt.plot([], [], 'o', label="Center", color='black')


    plt.legend(framealpha=1, loc='upper left')
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig('Images/Paper/Environment.png', dpi=600, bbox_inches='tight')

    # plt.show()

def figure_behavior_step_by_step():
    #----------------- DATA -----------------
    data_patha = 'Images\Data\Data_Behavior.json'

    with open(data_patha, 'r') as file:
        data = json.load(file)
    
    board_size = data['BOARD_SIZE']
    tile_size = data['TILE_SIZE']
    shape = data['SHAPE']
    resolution = data['RESOLUTION']
    target_center = np.array(data['TARGET_CENTER'])
    target_angle = data['TARGET_ANGLE']

    tetro_positions = np.array([np.array(data['object_center_x']), np.array(data['object_center_y'])]).T
    tetro_angles = np.array(data['object_angle'])
    
    print(tetro_positions)

    vectors_translation = np.array(data['vectors_translation'])
    vectors_rotation = np.array(data['vectors_rotation'])
    vectors = np.array(data['vectors'])

    signals_A = np.array(data['signals_A'])
    signals_B = np.array(data['signals_B'])

    
    #----------------- PLOT -----------------
    N, M = board_size, board_size

    n_steps = 3
    step_indexes = np.linspace(0, len(vectors), n_steps, dtype=int, endpoint=False)
    symbol = shape
    vertex = tetros_dict[symbol]

    target = Tetromino(vertex, resolution, COLORS.TARGET)
    target.angle = target_angle
    target.center = target_center/tile_size
    tetrom = Tetromino(vertex, resolution, COLORS.OBJECT)
    
    for step in range(n_steps):
        plt.figure(figsize=(5, 5))

        #GRID
        for i in range(N):
            for j in range(M):
                plt.plot([i, i+1], [j, j], COLORS.GRID)
                plt.plot([i, i], [j, j+1], COLORS.GRID)
                plt.plot([i, i+1], [j+1, j+1], COLORS.GRID)
                plt.plot([i+1, i+1], [j, j+1], COLORS.GRID)
                plt.plot(i+0.5, j+0.5, 'x', color=COLORS.GRID)

    
        #TARGET
        target.plot(plot=plt, text='$\\beta$', dtx=0.25, dty=0.25, hide_angle=True)
        
        #TETRO
        tetrom.angle = tetro_angles[step_indexes[step]]
        tetrom.center = tetro_positions[step_indexes[step]]/tile_size
        tetrom.plot(plot=plt, text='$\\alpha$', dtx=0.3, dty=0.15, hide_angle=True)
         
        
        contact_tiles(tetrom.polygon, N, COLORS.CONTACT_TILE, linestyle='-')
        contact_tiles(target.polygon, N, COLORS.TARGET_TILE, linestyle='--')

        #plt.plot([], [], 's', label="Object", color=COLORS.OBJECT)
        #plt.plot([], [], 's', label="Target position", color=COLORS.TARGET)
        #plt.plot([], [], '-', label="Contact tiles", color=COLORS.CONTACT_TILE)
        #plt.plot([], [], '--', label="Target tiles", color=COLORS.TARGET_TILE)
        #plt.plot([], [], 'x', label="Sensor", color=COLORS.GRID)
        #plt.plot([], [], 'o', label="Center", color='black')


        #plt.legend(framealpha=1, loc='upper left')
        plt.axis('off')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.tight_layout()
        plt.savefig(f'Images/Paper/test_{step}.png', dpi=600, bbox_inches='tight')



def contact_tiles_from_data(ax:plt, tiles:np.array, color='black', linestyle='-'):
    N,N = tiles.shape
    grid = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if tiles[j, i] == 1:
                grid[j, i] = 1
                tile_coords = [(i, j), (i+1, j), (i+1, j+1), (i, j+1)]
                tile = Polygon(tile_coords)        
                points = tile.exterior.coords
                x_values, y_values = zip(*points)
                #ax.fill(x_values, y_values, color=color, alpha=0.9, zorder=2)
                ax.plot(x_values, y_values, color=color, linestyle=linestyle, linewidth=2, zorder=2)

    for i in range(N):
        for j in range(N):
            if grid[j, i] != 1:
                up = grid[j-1, i] if j > 0 else 0
                down = grid[j+1, i] if j < N-1 else 0
                left = grid[j, i-1] if i > 0 else 0
                right = grid[j, i+1] if i < N-1 else 0

                if up + down + left + right > 0:
                    tile = Polygon([(i, j), (i+1, j), (i+1, j+1), (i, j+1)])
                    points = tile.exterior.coords
                    x_values, y_values = zip(*points)
                    #ax.fill(x_values, y_values, color=color, alpha=0.9, zorder=2)
                    ax.plot(x_values, y_values, color=color, linestyle='dotted', linewidth=2, zorder=2)

def figure_behavior_multistep():
    #----------------- DATA -----------------
    data_patha = 'Images\Data\Data_Behavior.json'

    with open(data_patha, 'r') as file:
        data = json.load(file)
    
    board_size = data['BOARD_SIZE']
    tile_size = data['TILE_SIZE']
    shape = data['SHAPE']
    resolution = data['RESOLUTION']
    
    target_center = np.array(data['TARGET_CENTER'])
    target_angle = data['TARGET_ANGLE']

    target_tiles = np.array(data['TARGET_TILES'])
    contact_tiles = np.array(data['contacts'])
    
    tetro_positions = np.array([np.array(data['object_center_x']), np.array(data['object_center_y'])]).T
    tetro_angles = np.array(data['object_angle'])
    tetro_polygons = data['TETROMINO_POLYGON']
    for i in range(len(tetro_polygons)):
        tetro_polygons[i] = np.array(tetro_polygons[i])

    polygon_target = np.array(data['TARGET_POLYGON'])
    vectors_translation = np.array(data['vectors_translation'])
    vectors_rotation = np.array(data['vectors_rotation'])
    vectors = np.array(data['vectors'])

    signals_A = np.array(data['signals_A'])
    #signals_B = np.array(data['signals_B'])

    
    #----------------- PLOT -----------------
    N, M = board_size, board_size

    n_steps = 4
    step_indexes = np.linspace(1, len(vectors), n_steps, dtype=int, endpoint=False)
    print(step_indexes)

    step_indexes = [ 1, 15, 30, 45 ]
    print(step_indexes)

    
    polygon_target = polygon_target/(tile_size*resolution)
    polygon_target_center = np.mean(polygon_target, axis=0)
    polygon_target = polygon_target + target_center/(tile_size*resolution) - polygon_target_center
    target = Tetromino(polygon_target, resolution, COLORS.TARGET)
        



    target_tiles = np.reshape(target_tiles, (N, N))

    fig, axes = plt.subplots(1, n_steps, figsize=(n_steps * 4, 4))

    for step, ax in zip(range(n_steps), axes):
        #GRID
        for i in range(N):
            for j in range(M):
                ax.plot([i, i+1], [j, j], COLORS.GRID)
                ax.plot([i, i], [j, j+1], COLORS.GRID)
                ax.plot([i, i+1], [j+1, j+1], COLORS.GRID)
                ax.plot([i+1, i+1], [j, j+1], COLORS.GRID)
                #ax.plot(i+0.5, j+0.5, 'x', color=COLORS.GRID)

    
        #TARGET AND TETRO
        polygon_tetro = tetro_polygons[step_indexes[step]]/(tile_size*resolution)
        polygon_tetro_center = np.mean(polygon_tetro, axis=0)
        polygon_tetro = polygon_tetro  + tetro_positions[step_indexes[step]]/(tile_size*resolution) - polygon_tetro_center
        tetrom = Tetromino(polygon_tetro, resolution, COLORS.OBJECT)
        
        #tetrom.angle = tetro_angles[step_indexes[step]]
        #tetrom.center = tetro_positions[step_indexes[step]]/tile_size 

        draw_tetro(target, ax)
        draw_tetro(tetrom, ax)
        
        contact_tiles_from_data(ax, target_tiles, COLORS.TARGET_TILE, linestyle='-')
        #contact_tiles_from_data(ax, contacts, COLORS.TARGET_TILE, linestyle='-')
        
        #plot signal_A
        signal_A = signals_A[step_indexes[step]]
        signal_A = signal_A.reshape(N, M)
        ax.imshow(signal_A, cmap=cm.Greys, alpha=0.5, zorder=-1, extent=[0, N, 0, M], origin='lower')
        
        #plot signal_B
        #signal_B = signals_B[step_indexes[step]]
        #signal_B = signal_B.reshape(N, M)
        #ax.imshow(signal_B, cmap=cm.Greys, alpha=0.5, zorder=-1, extent=[0, N, 0, M], origin='lower')
        

        # Plot vectors in a quiver plot for tiles in contact
        contacts = np.reshape(contact_tiles[step_indexes[step]], (N, N))
        #print(contacts.shape)
        x = np.arange(0, N, 1) + 0.5
        y = np.arange(0, M, 1) + 0.5
        
        X, Y = np.meshgrid(x, y)
        #print(X.shape, Y.shape)
        U, V = vectors[step_indexes[step]].T

        ax.quiver(X, Y, U, V, scale=2, scale_units='xy', angles='xy', color='black', zorder=3, width=0.006)
        
      
        #set limits
        X0,X = [5, N-6]
        Y0,Y = [6, M-5]
        ax.set_xlim([X0, X])
        ax.set_ylim([Y0, Y])

        #add black border
        ax.plot([X0, X], [Y0, Y0], 'k', linewidth=2)
        ax.plot([X0, X], [Y, Y], 'k', linewidth=2)
        ax.plot([X0, X0], [Y0, Y], 'k', linewidth=2)
        ax.plot([X, X], [Y0, Y], 'k', linewidth=2)

        
        ax.axis('off')
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f'Step {step_indexes[step]}', size = 20)

    plt.tight_layout()
    plt.savefig('Images/Paper/Behavior.png', dpi=600, bbox_inches='tight')





if __name__ == '__main__':
    #figure_environment()
    figure_behavior_multistep()
