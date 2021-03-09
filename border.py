import bpy
from bpy.types import (
    Curve,
)
from mathutils import (geometry, Vector)
import numpy

from . import grid
from . import bezier
import importlib
grid = importlib.reload(grid)
bezier = importlib.reload(bezier)

def is_valid_curve(curve):
    if curve.dimensions != '2D' or len(curve.splines) != 1:
        return False
    spline = curve.splines[0]
    
    if len(spline.bezier_points) < 2:
        return False
    points = spline.bezier_points
    
    return points[len(points)-1].co.x - points[0].co.x > 0

def to_3d(point):
    return Vector((point.x, 0, point.y))

class Border:
    def __init__(self, cubics = None):
        self.cubics = [] if cubics is None else cubics
    
    @staticmethod
    def from_curve(curve, flip=False):
        border = Border()
        points = curve.splines[0].bezier_points
        for p0, p1 in zip(points[:-1], points[1:]):
            border.cubics.append(bezier.Cubic(p0.co.xy, p0.handle_right.xy, p1.handle_left.xy, p1.co.xy))
        
        if flip:
            border.__reverse()
            for cubic in border.cubics:
                cubic.scale((0,), (-1,))
        
        translation = -border.cubics[0].p
        for cubic in border.cubics:
            cubic.translate(translation)
        
        return border
    
    @property
    def is_flat(self):
        ref = self.cubics[0].p.y
        return all(all(abs(point.y - ref) < 0.0001 for point in cubic.points) for cubic in self.cubics)
    
    @property
    def size(self):
        return self.cubics[-1].q.copy()
    
    @property
    def length(self):
        return self.size.x
    
    @property
    def grid_length(self):
        return grid.to_grid_length(self.length)
    
    @property
    def height(self):
        return self.size.y
    
    @property
    def grid_height(self):
        return grid.to_grid_length(self.height)
    
    def __reverse(self):
        for cubic in self.cubics:
            cubic.reverse()
        self.cubics.reverse()
    
    def flip(self):
        raise 'DEPRECATED'
        translation = self.cubics[-1].q.x
        for cubic in self.cubics:
            for point in cubic.points:
                point.x = -point.x + translation
            cubic.reverse()
        self.cubics.reverse()
            
    
    def sample(self, grid_subdivisions, precision, epsilon=0.0001):
        cubics = bezier.subdivide(self.cubics, precision)
        points = []
        step = grid.length / grid_subdivisions
        x = 0
        last_cubic_index = 0
        length = self.length
        while x + epsilon < length:
            for cubic_index, cubic in enumerate(cubics[last_cubic_index:]):
                if cubic[0].x <= x and x < cubic[3].x:
                    last_cubic_index = cubic_index
                    y = cubic[0].y
                    if x != cubic[0].x:
                        y = cubic[0].y + (cubic[3].y - cubic[0].y) / (cubic[3].x - cubic[0].x) * (x - cubic[0].x)
                    points.append(Vector((x, y)))
                    break
            x += step
        points.append(self.cubics[-1][3].xy)
        return points
        
    def to_curve(self, name='Curve'):
        curve = bpy.data.curves.new(name, type='CURVE')
        curve.dimensions = '3D'
        spline = curve.splines.new('BEZIER')
        points = spline.bezier_points
        points[0].co = to_3d(self.cubics[0].p)
        points[0].handle_right = to_3d(self.cubics[0].r)
        v = points[0].handle_right - points[0].co
        points[0].handle_left = points[0].co - v
        
        for i in range(len(self.cubics)-1):
            points.add(1)
            point = points[-1]
            point.handle_left = to_3d(self.cubics[i].l)
            point.co = to_3d(self.cubics[i].q)
            point.handle_right = to_3d(self.cubics[i+1].r)
        
        points.add(1)
        points[-1].co = to_3d(self.cubics[-1].q)
        points[-1].handle_left = to_3d(self.cubics[-1].l)
        v = points[-1].handle_left - points[-1].co
        points[-1].handle_right = points[-1].co - v
        return curve
    
    def resized(self, new_height, keep_tangents=True):
        diff = new_height - self.size[1]
        length = self.length
        cubics = []
        for cubic_index, cubic in enumerate(self.cubics):
            dp = cubic.p.x / length * diff
            dr = cubic.r.x / length * diff
            dl = cubic.l.x / length * diff
            dq = cubic.q.x / length * diff
            if keep_tangents and cubic_index == 0:
                dr = dp
            if keep_tangents and cubic_index+1 == len(self.cubics):
                dl = dq
                
            cubics.append(bezier.Cubic(
                cubic.p + Vector((0, dp)),
                cubic.r + Vector((0, dr)),
                cubic.l + Vector((0, dl)),
                cubic.q + Vector((0, dq))
            ))
        return Border(cubics)







