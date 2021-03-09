from mathutils import (geometry, Vector)
from copy import copy

class Cubic():
    def __init__(self, p0=[Vector(),Vector(),Vector(),Vector()], p1=None, p2=None, p3=None):
        if not type(p0) is tuple:
            p0 = [p0, p1, p2, p3]
        self.points = p0
    
    def __getitem__(self, key):
        return self.points[key]
    
    def __setitem__(self, key, value):
        self.points[key] = value
    
    def copy(self):
        return copy(self)
    
    def __copy__(self):
        return Cubic(self.points[0].copy(), self.points[1].copy(), self.points[2].copy(), self.points[3].copy())
    
    def __repr__(self):
        return 'Cubic({}, {}, {}, {})'.format(*self.points)
    
    @property
    def p(self):
        return self[0]
    
    @p.setter
    def p(self, value):
        self[0] = value
    
    @property
    def r(self):
        return self[1]
    
    @r.setter
    def r(self, value):
        self[1] = value
    
    @property
    def l(self):
        return self[2]
    
    @l.setter
    def l(self, value):
        self[2] = value
    
    @property
    def q(self):
        return self[3]
    
    @q.setter
    def q(self, value):
        self[3] = value
    
    def translate(self, translation):
        for i in range(len(self.points)):
            self.points[i] = self.points[i] + translation
    
    def scale(self, pivot, factor):
        for point in self.points:
            for i in range(len(factor)):
                point[i] = pivot[i] + factor[i] * (point[i] - pivot[i])
    
    def evaluate(self, t):
        u = 1 - t
        return u*u*u * self[0] + 3*u*u*t * self[1] + 3*u*t*t * self[2] + t*t*t * self[3]
    
    def reversed(self):
        return Cubic(self.points[::-1])
    
    def reverse(self):
        self.points = self.points[::-1]
        
    def split(self, t=0.5):
        q = self.evaluate(t)
        u = 1 - t
        c0 = u * u
        c1 = 2 * t * u
        c2 = t * t
        p1b = self[0] + t * (self[1] - self[0])
        p2b = self[3] + u * (self[2] - self[3])
        l = c0 * self[0] + c1 * self[1] + c2 * self[2]
        r = c0 * self[1] + c1 * self[2] + c2 * self[3]
        return [Cubic(self[0], p1b, l, q), Cubic(q, r, p2b, self[3])]
    
    def subdivide(self, num_cuts=1):
        subdivisions = [self.copy()]
        for i in range(num_cuts):
            subdivisions.extend(subdivisions.pop().split(1/(num_cuts+1-i)))
        return subdivisions
    
def subdivide(cubics, num_cuts=1):
    return [new_cubic for cubic in cubics for new_cubic in cubic.subdivide(num_cuts)]
