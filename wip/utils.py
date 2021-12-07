import bpy

def create_line_mesh(length=1, subdivisions=1, thickness=0):
    mesh = bpy.data.meshes.new('Line')
    offset = thickness / 2
    length = length + 2 * offset
    vertices = [(-offset + (i / subdivisions) * length, -offset, 0.0) for i in range(subdivisions+1)]
    edges = []
    faces = []
    
    if thickness == 0:
        edges = [(i, i+1) for i in range(subdivisions)]
    else:
        vertices.extend([(-offset + (i / subdivisions) * length, offset, 0.0) for i in range(subdivisions+1)])
        faces = [(i, i+1, i+subdivisions+1, i+subdivisions+2) for i in range(subdivisions)]
    
    mesh.from_pydata(vertices, edges, faces)
    return mesh

