from matplotlib import pyplot as plt
import numpy as np
import numpy as np

#SHAPES ----------------
tetros_dict = {
'L' : np.array([(0, 0), (0, 3), (1, 3), (1, 1), (2, 1), (2, 0)]),
'O' : np.array([(0, 0), (0, 2), (2, 2), (2, 0)]),
'T' : np.array([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 1), (3, 1), (3, 0)]),
'I' : np.array([(0, 0), (0, 1), (4, 1), (4, 0)]),
'S' : np.array([(0, 0), (0, 1), (1, 1), (1, 2), (3, 2), (3, 1), (2, 1), (2, 0)]),
'Z' : np.array([(0, 2), (2, 2), (2, 1), (3, 1), (3, 0), (1, 0), (1, 1), (0, 1)]),
'J' : np.array([(0, 0), (0, 1), (1, 1), (1, 3), (2, 3), (2, 0)]),
}

tetrominos = list(tetros_dict.values())

def _create_circle():
    n = 50
    radius = 1
    angles = np.linspace(0, 2 * np.pi, n + 1)[:-1]
    xs = radius * np.cos(angles)
    ys = radius * np.sin(angles)

    shape = np.array([xs, ys]).T
    return shape


def _create_empty_circle():
    n = 50
    radius = 1.5
    inner_radius = 0.75
    pad = 0

    out_ring = np.linspace(0, 2 * np.pi - pad, n + 1)[:-1]
    xs = radius * np.cos(out_ring)
    ys = radius * np.sin(out_ring)

    in_ring = np.linspace(0, 2 * np.pi - pad, n + 1)[:-1]
    xs_in = inner_radius * np.cos(in_ring)
    ys_in = inner_radius * np.sin(in_ring)

    xs = [*xs, *xs_in[::-1]]
    ys = [*ys, *ys_in[::-1]]

    shape = np.array([xs, ys]).T
    return shape


unknown_shapes_dict = {
    'P3' : np.array([(1.0, 0.8660254037844385), (-0.4999999999999998, 1.7320508075688772), (-0.5000000000000004, 0.0), (1.0, 0.8660254037844383)])*3/2,
    'P5' : np.array([(1.0, 0.0), (0.30901699437494745, 0.9510565162951535), (-0.8090169943749473, 0.5877852522924732), (-0.8090169943749475, -0.587785252292473), (0.30901699437494723, -0.9510565162951536), (1.0, -2.4492935982947064e-16)])*4/3,
    'C' : _create_circle(),
    'R' : _create_empty_circle(),
    'L2' : np.array([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 0)])*1.5,
    'L3' : np.array([(0, 0), (0, 1), (-1,1), (-1,2),(0,2),(0,3), (1, 3), (1, 1), (2, 1), (2, 0)]),
    'U' : np.array([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (1.3333333333333333, 2.0), (1.3333333333333333, 0.6666666666666666), (0.6666666666666666, 0.6666666666666666), (0.6666666666666666, 2.0), (0.0, 2.0)])*3/2,
    }

unknown_shapes = list(unknown_shapes_dict.values())


def get_name(vertex:list[list]):
    for name, shape in unknown_shapes_dict.items():
        if np.array_equal(shape, vertex):
            return name
    for name, shape in tetros_dict.items():
        if np.array_equal(shape, vertex):
            return name
    raise Exception('Shape not found')

if __name__ == '__main__':
    pass

if __name__ == '__main__':
    from _colors import create_palette
    
    shapes_groups = [tetros_dict]
    
    for n, group in enumerate(shapes_groups):
    
        previous_origin = -0.5
        x_max = 0
        y_max = 0

        shapes = list(group.values())
        names = list(group.keys())
        palette  = create_palette(len(shapes))


        tick_positions = []
        for i in range(len(shapes)):
            shape = shapes[i]

            shape[:, 1] = shape[:, 1] - min(shape[:, 1])
            shape[:, 0] = shape[:, 0] - min(shape[:, 0])

            shape = shape + [previous_origin + 0.5, 0]
            
            previous_origin = max(shape[:, 0])
            
            xs, ys = shape[:, 0], shape[:, 1]
            xs = [*xs, xs[0]]
            ys = [*ys, ys[0]]  

            x_max = max(x_max, max(xs))
            y_max = max(y_max, max(ys))

            shape_center = np.mean(shape, axis=0)
            tick_positions.append(shape_center[0])

            plt.plot(xs, ys, color='black', linewidth=1.5, zorder=2)
            plt.fill(xs, ys, color=palette[i], alpha=1, zorder=1)

        pad = 0.25
        plt.xlim(0 - pad, x_max + pad)
        plt.ylim(0 - pad, y_max + pad)
        
        plt.xticks(tick_positions, names, rotation=0)

        #plt.axis('off')
        #set y axis False
        plt.gca().axes.get_yaxis().set_visible(False)
        plt.gca().set_aspect('equal', adjustable='box')
        
        #ticks font size
        plt.xticks(fontsize=12)
        plt.tight_layout()
        path_image = f'Images/Paper/Shapes.png'
        plt.savefig(path_image, dpi=600, bbox_inches='tight', pad_inches=0, transparent=False)
        #plt.show()
        plt.clf()