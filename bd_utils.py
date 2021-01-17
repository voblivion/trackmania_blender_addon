import bpy
from mathutils import Vector

def get_objects_bounds(objects):
    return [object.matrix_world @ Vector(tuple(pos)) for object in objects for pos in object.bound_box]

def get_vectors_center(vectors):
    lower = vectors[0].copy()
    upper = vectors[0].copy()
    for vector in vectors:
        for i in range(len(vector)):
            lower[i] = min(lower[i], vector[i])
            upper[i] = max(upper[i], vector[i])
    return (lower + upper) / 2

def inverse_matrix(matrix):
    copy = matrix.copy()
    copy.invert()
    return copy