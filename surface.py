import bpy
from bpy.types import (
    AddonPreferences,
    Curve,
    Material,
    Menu,
    Object,
    Operator,
    Panel,
    PropertyGroup,
    UIList
)
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty
)
from mathutils import Vector
from random import random
from math import (radians)
from contextlib import redirect_stdout
import io

from . import border

# HACK reload
import importlib
border = importlib.reload(border)

# Properties
class SCENE_PG_BorderSettings(PropertyGroup):
    bl_idname = 'SCENE_PG_BorderSettings'
    
    flip: BoolProperty(
        name='Flip?',
        description='Whether or not this border is flipped from its default orientation'
    )
    
    def validate_curve(self, curve):
        return border.is_valid_curve(curve)
    
    curve: PointerProperty(
        type=Curve,
        name='Curve',
        description='2D curve defining shape of border.',
        poll=validate_curve
    )


def draw_border(layout, border, name):
    layout.ui_units_x = 0.8
    row = layout.row(align=True)
    row = row.split(factor=0.23, align=True)
    row.label(text=name + ':')
    row = row.split(factor=0.8, align=True)
    row.prop(border, 'curve', text='')
    row.prop(border, 'flip')

def generate_surface_screw(context):
    scene = context.scene
    settings = scene.trackmania_surface_settings
    print('generating screw surface')
    pass

def create_pivot(context, name):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'PLAIN_AXES'
    obj.trackmania_pivot.is_pivot = True
    context.scene.collection.objects.link(obj)
    return obj
    

def generate_surface_connector(context):
    scene = context.scene
    settings = scene.trackmania_surface_settings
    object = settings.surface
    
    # East border
    if settings.border_0.curve is None:
        return 'East border is not set'
    if not border.is_valid_curve(settings.border_0.curve):
        return 'East border is invalid'
    east_border = border.Border.from_curve(settings.border_0.curve, settings.border_0.flip)
    
    # West border
    if settings.border_1.curve is None:
        return 'West border is not set'
    if not border.is_valid_curve(settings.border_1.curve):
        return 'West border is invalid'
    west_border = border.Border.from_curve(settings.border_1.curve, settings.border_1.flip)
    
    # East & West points
    east_west_subdivisions = settings.grid_subdivisions_flat if (east_border.is_flat and west_border.is_flat) else settings.grid_subdivisions_curved
    east_points = east_border.sample(east_west_subdivisions, settings.bezier_precision)
    west_points = west_border.sample(east_west_subdivisions, settings.bezier_precision)
    m = len(east_points)
    
    # North border
    if settings.border_2.curve is None:
        return 'North border is not set'
    if not border.is_valid_curve(settings.border_2.curve):
        return 'North border is invalid'
    north_border = border.Border.from_curve(settings.border_2.curve, settings.border_2.flip)
    
    # South border
    if settings.border_3.curve is None:
        return 'South border is not set'
    if not border.is_valid_curve(settings.border_3.curve):
        return 'South border is invalid'
    south_border = border.Border.from_curve(settings.border_3.curve, settings.border_3.flip)
    
    # North & South points
    north_south_subdivisions = settings.grid_subdivisions_flat if (north_border.is_flat and south_border.is_flat) else settings.grid_subdivisions_curved
    north_points = north_border.sample(north_south_subdivisions, settings.bezier_precision)
    south_points = south_border.sample(north_south_subdivisions, settings.bezier_precision)
    n = len(north_points)

    
    # Validate borders join
    epsilon = 0.001
    x_diff = abs(east_border.size.x - west_border.size.x)
    if x_diff > epsilon:
        return 'East and West borders have different length: {}'.format(x_diff)
    
    y_diff = abs(north_border.size.x - south_border.size.x)
    if y_diff > epsilon:
        return 'North and South borders have different length: {}'.format(y_diff)
    
    z_diff = abs(east_border.size.y - west_border.size.y + north_border.size.y - south_border.size.y)
    if z_diff > epsilon:
        return 'Borders cannot join in altitude: {}'.format(z_diff)
    
    # Blend borders
    vertices = []
    faces = []
    for i, east_point in enumerate(east_points):
        west_point = west_points[i]
        blend_factor = i / (len(east_points) - 1)
        
        north_border_cpy = north_border.resized(west_point.y + south_border.size.y - east_point.y)
        south_border_cpy = south_border.resized(west_point.y + south_border.size.y - east_point.y)
        offset = Vector((0, east_point.y))
        
        north_points_cpy = [point + offset for point in north_border_cpy.sample(north_south_subdivisions, settings.bezier_precision)]
        south_points_cpy = [point + offset for point in south_border_cpy.sample(north_south_subdivisions, settings.bezier_precision)]
        '''
        2---------i+2----------
        |\          \          \
        | \          \          \
        |  1---------i+1---------\
        5  |\          \          \
         \ | \          \          \
          \|  \          \          \
           4   0----------i----------\
            \  |          |          |
             \ |          |          |
              \|          |          |
               3---------i+3----------
        '''
        vertices.extend([Vector((
            east_point.x,
            blend_factor * north_point.x + (1 - blend_factor) * south_point.x,
            blend_factor * north_point.y + (1 - blend_factor) * south_point.y + settings.height
        )) for north_point, south_point in zip(north_points_cpy, south_points_cpy)])
        
        vertices.extend([Vector((
            east_point.x,
            blend_factor * north_point.x + (1 - blend_factor) * south_point.x,
            blend_factor * north_point.y + (1 - blend_factor) * south_point.y
        )) for north_point, south_point in zip(north_points_cpy, south_points_cpy)])
        
        if i == 0:
            n = len(north_points)
            faces.extend([(j, j+1, j+n+1, j+n) for j in range(n - 1)])
        
        if i != 0:
            n = len(north_points)
            faces.extend([((i - 1) * (n * 2) + j, i * (n * 2) + j, i * (n * 2) + j + 1, (i - 1) * (n * 2) + j + 1) for j in range(n - 1)])
            faces.extend([((i - 1) * (n * 2) + j + n, (i - 1) * (n * 2) + j + n + 1, i * (n * 2) + j + n + 1, i * (n * 2) + j + n) for j in range(n - 1)])
            faces.append(((i-1)*n*2,(i-1)*n*2+n,i*n*2+n,i*n*2))
            faces.append(((i-1)*n*2+n+n-1,(i-1)*n*2+n-1,i*n*2+n-1,i*n*2+n+n-1))
        
        if i == len(east_points) - 1:
            faces.extend([(i*n*2+j, i*n*2+j+n, i*n*2+j+n+1, i*n*2+j+1) for j in range(n - 1)])
    
    # Offset Z so lowest corner at 0
    z_corners = [0, east_border.size.y, east_border.size.y + north_border.size.y, south_border.size.y]
    offset = Vector((0, 0, -min(z_corners)))
    for vertice in vertices: vertice += offset
    
    # Replace current surface mesh
    mesh = bpy.data.meshes.new('Surface')
    mesh.from_pydata(vertices, [], faces)
    if settings.top_material is None:
        settings.top_material = bpy.data.materials.new('TopMaterial')
    mesh.materials.append(settings.top_material)
    if settings.bottom_material is None:
        settings.bottom_material = bpy.data.materials.new('BottomMaterial')
    mesh.materials.append(settings.bottom_material)
    if settings.side_material is None:
        settings.side_material = bpy.data.materials.new('SideMaterial')
    mesh.materials.append(settings.side_material)
    old_mesh = object.data
    object.data = mesh
    bpy.data.meshes.remove(old_mesh)
    
    # Set Pivots
    if settings.pivot_0 is None:
        settings.pivot_0 = create_pivot(context, 'Pivot_0')
    settings.pivot_0.location = object.matrix_world @ mesh.vertices[n].co
    if settings.pivot_1 is None:
        settings.pivot_1 = create_pivot(context, 'Pivot_1')
    settings.pivot_1.location = object.matrix_world @ mesh.vertices[2*n*(m-1)+n].co
    if settings.pivot_2 is None:
        settings.pivot_2 = create_pivot(context, 'Pivot_2')
    settings.pivot_2.location = object.matrix_world @ mesh.vertices[2*n*(m-1)+2*n-1].co
    if settings.pivot_3 is None:
        settings.pivot_3 = create_pivot(context, 'Pivot_3')
    settings.pivot_3.location = object.matrix_world @ mesh.vertices[2*n-1].co
    
    # Set Base Material's UV
    uv_base_material = mesh.uv_layers.new(name='BaseMaterial')
    mesh.uv_layers.active = uv_base_material
    for f in range(len(mesh.polygons)):
        face = mesh.polygons[f]
        if (f - (n - 1)) % (2 * (n - 1) + 2) < n - 1:
            face.material_index = 0
        else:
            face.material_index = 1
        for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
            vertex = mesh.vertices[vertex_id]
            uv_base_material.data[loop_id].uv = (vertex.co[0] / 32, vertex.co[1] / 32)
    for i in range(m-1):
        fs = [
            (n - 1) + (2 * (n - 1) + 2) * i + 2 * n - 1,
            (n - 1) + (2 * (n - 1) + 2) * i + 2 * n - 2
        ];
        for f in fs:
            face = mesh.polygons[f];
            face.material_index = 2
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                p = 0
                if vertex_id % n != 0:
                    p = 1
                z = 0
                if ((vertex_id + p)/n) % 2 == p:
                    z = settings.height
                uv_base_material.data[loop_id].uv = (vertex.co[0] / 32, z / 32)
    for j in range(n-1):
        fs = [j, n - 1 + (2 * (n - 1) + 2) * (m - 1) + j]
        for f in fs:
            face = mesh.polygons[f]
            face.material_index = 2
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                z = 0
                if vertex_id % (2 * n * (m - 1)) < n:
                    z = settings.height
                uv_base_material.data[loop_id].uv = (vertex.co[1] / 32, z / 32)
    
    # Set Normals & Lightmap's UV
    uv_lightmap = mesh.uv_layers.new(name='Lightmap')
    mesh.uv_layers.active = uv_lightmap
    margin = settings.lightmap_margin / 100 * 0.25 / 2
    for f in range(len(mesh.polygons)):
        face = mesh.polygons[f]
        if f < n-1: # Front face
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = 0.5 + margin
                if vertex_id % (2 * n * (m - 1)) >= n:
                    x += 0.25 - 2 * margin
                y = 0.5 + margin + (vertex.co[1] / north_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        elif f >= (n-1) + (2 * (n-1) + 2) * (m-1): # Back face
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = 0.75 + margin
                if vertex_id % (2 * n * (m - 1)) >= n:
                    x += 0.25 - 2 * margin
                y = 0.5 + margin + (vertex.co[1] / north_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        elif (f - (n - 1)) % (2 * (n - 1) + 2) < n - 1: # Top face
            face.use_smooth = True
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = margin + (vertex.co[0] / east_border.length) * (0.5 - 2 * margin)
                y = margin + (vertex.co[1] / north_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        elif (f - (n - 1)) % (2 * (n - 1) + 2) < 2 * (n - 1): # Bottom face
            face.use_smooth = True
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = margin + (vertex.co[0] / east_border.length) * (0.5 - 2 * margin)
                y = 0.5 + margin + (vertex.co[1] / north_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        elif (f - (n - 1)) % (2 * (n - 1) + 2) >= 2 * (n - 1) + 1: # Right face
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = 0.5 + margin
                if ((vertex_id+1) / n) % 2 == 0:
                    x += 0.25 - 2 * margin
                y = 0.0 + margin + (vertex.co[0] / east_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        else: # Left face
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = 0.75 + margin
                if (vertex_id / n) % 2 == 0:
                    x += 0.25 - 2 * margin
                y = 0.0 + margin + (vertex.co[0] / east_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
    
    # Set Item settings
    scene.trackmania_item.ghost_mode = True
    scene.trackmania_item.fly_step = 8
    scene.trackmania_item.grid_horizontal_step = 32
    scene.trackmania_item.grid_vertical_step = 8
    

def generate_surface(context):
    scene = context.scene
    settings = scene.trackmania_surface_settings
    if settings.surface is None:
        mesh = context.blend_data.meshes.new(scene.name)
        object = context.blend_data.objects.new(scene.name, mesh)
        scene.collection.objects.link(object)
        settings.surface = object
    
    if settings.surface_type == 'SCREW':
        return generate_surface_screw(context)
    elif settings.surface_type == 'CONNECTOR':
        return generate_surface_connector(context)
    
    return 'Surface type is None'

class SCENE_PG_SurfaceSettings(PropertyGroup):
    bl_idname = 'SCENE_PG_SurfaceSettings'
    
    def __init__(self):
        super().__init__()
        for _ in range(4):
            self.borders.add()
    
    def update(self, context):
        if self.enable_continuous_update:
            generate_surface(context, self.id_data)
       
    enable_continuous_update: BoolProperty(
        name='Enable Continuous Update',
        description='When set, will update shape whenever one of its attributes is changed',
        default=False,
        update=update
    ) 
        

    # Common properties
    surface_type: EnumProperty(
        name='Type',
        description='How the surface is generated',
        items=(
            ('NONE', 'None', 'No surface generated'),
            ('SCREW', 'Screw', 'Translate and/or rotate a border'),
            ('CONNECTOR', 'Connector', 'Connect 4 borders')),
        update=update
    )
    
    grid_subdivisions_flat: IntProperty(
        name='Flat Subdivisions',
        description='Number of subdivisions per grid unit when surface is flat (TM vanilla uses 4)',
        min=1,
        soft_max=16,
        default=4,
        update=update
    )
    
    grid_subdivisions_curved: IntProperty(
        name='Curved Subdivisions',
        description='Number of subdivisions per grid unit when surface is curved (TM vanilla uses 32)',
        min=1,
        soft_max=64,
        default=32,
        update=update
    )
    
    height: FloatProperty(
        name='Height',
        description='How high surface is compared to ground',
        min=0,
        max=8,
        default=2,
        update=update
    )
    
    bezier_precision: IntProperty(
        name='Bezier Precision',
        description='How many time bezier curved is sambled before surface is projected on it',
        min=0,
        soft_max=256,
        default=128,
        update=update
    )
    
    lightmap_margin: FloatProperty(
        name='Lightmap Margin (%)',
        description='Island margin for Lightmap UV unwrapping',
        min=0,
        max=100,
        default=10,
        update=update
    )
    
    top_material: PointerProperty(
        type=Material,
        name='Top Material',
        description='Material of generated top surface'
    )
    
    bottom_material: PointerProperty(
        type=Material,
        name='Bottom Material',
        description='Material of generated bottom surface'
    )
    
    side_material: PointerProperty(
        type=Material,
        name='Side Material',
        description='Material of generated side surfaces'
    )
    
    border_0: PointerProperty(
        type=SCENE_PG_BorderSettings,
        name='Border 0',
        description='Border 0 of generated surface',
        update=update
    )
    
    border_1: PointerProperty(
        type=SCENE_PG_BorderSettings,
        name='Border 1',
        description='Border 1 of generated surface',
        update=update
    )
    
    border_2: PointerProperty(
        type=SCENE_PG_BorderSettings,
        name='Border 2',
        description='Border 2 of generated surface',
        update=update
    )
    
    border_3: PointerProperty(
        type=SCENE_PG_BorderSettings,
        name='Border 3',
        description='Border 3 of generated surface',
        update=update
    )
    
    surface: PointerProperty(type=Object)
    pivot_0: PointerProperty(type=Object)
    pivot_1: PointerProperty(type=Object)
    pivot_2: PointerProperty(type=Object)
    pivot_3: PointerProperty(type=Object)
    
    # Screw properties
    
    # Connector properties
    preserve_tangents: BoolProperty(
        name='Preserve Tangents',
        description='Whether or not border tangents must be preserved when ran across surface. Both opposit borders must have same tangents at their extremities for it to work'
    )


class SCENE_PG_MultiSurfaceMaterial(PropertyGroup):
    bl_idname = 'SCENE_PG_MultiSurfaceMaterial'
    
    material: PointerProperty(
        type=Material
    )
    
    export_name: StringProperty(name='Export Name')

class VIEW3D_OT_MultiSurfaceBordersEdit(Operator):
    bl_idname = 'scene.tm_multi_surface_borders_edit'
    bl_label = 'Multi Surface - Edit Borders'
    bl_options = {'REGISTER'}
    
    action: EnumProperty(
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', ''),
            ('REMOVE', 'Remove', ''),
            ('ADD', 'Add', '')
        )
    )
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def invoke(self, context, event):
        scene = context.scene
        settings = scene.trackmania_multi_surface
        index = settings.selected_border
        
        try:
            item = settings.borders[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(settings.borders) - 1:
                settings.borders.move(index, index+1)
                settings.selected_border += 1
            elif self.action == 'UP' and index >= 1:
                settings.borders.move(index, index-1)
                settings.selected_border -= 1
            elif self.action == 'REMOVE':
                settings.selected_border -= 1
                settings.borders.remove(index)
        
        if self.action == 'ADD':
            settings.borders.add()
        
        return {'FINISHED'}

class VIEW3D_UL_MultiSurfaceBorderItems(UIList):
    bl_idname = 'VIEW3D_UL_MultiSurfaceBorderItems'
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, 'curve')
        row.prop(item, 'flip')
    
    def invoke(self, context, event):
        pass

class VIEW3D_OT_MultiSurfaceMaterialsEdit(Operator):
    bl_idname = 'scene.tm_multi_surface_materials_edit'
    bl_label = 'Multi Surface - Edit Materials'
    bl_options = {'REGISTER'}
    
    action: EnumProperty(
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', ''),
            ('REMOVE', 'Remove', ''),
            ('ADD', 'Add', '')
        )
    )
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def invoke(self, context, event):
        scene = context.scene
        settings = scene.trackmania_multi_surface
        index = settings.selected_material
        
        try:
            item = settings.materials[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(settings.materials) - 1:
                settings.materials.move(index, index+1)
                settings.selected_material += 1
            elif self.action == 'UP' and index >= 1:
                settings.materials.move(index, index-1)
                settings.selected_material -= 1
            elif self.action == 'REMOVE':
                settings.selected_material -= 1
                settings.materials.remove(index)
        
        if self.action == 'ADD':
            settings.materials.add()
        
        return {'FINISHED'}

class VIEW3D_UL_MultiSurfaceMaterialItems(UIList):
    bl_idname = 'VIEW3D_UL_MultiSurfaceMaterialItems'
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, 'material', text='')
        row.prop(item, 'export_name', text='Name')
    
    def invoke(self, context, event):
        pass

class SCENE_PG_MultiSurfaceSettings(PropertyGroup):
    bl_idname = 'SCENE_PG_MultiSurfaceSettings'
    
    borders: CollectionProperty(
        type=SCENE_PG_BorderSettings,
        name='Borders'
    )
    selected_border: IntProperty()
    
    materials: CollectionProperty(
        type=SCENE_PG_MultiSurfaceMaterial
    )
    selected_material: IntProperty()
    
    simplify_threshold: FloatProperty(
        name='Simplify Threshold',
        description='Deviation angle within witch 2 adjacent faces are considered co-planar',
        min=0,
        max=180,
        default=1
    )

class VIEW3D_OT_MultiSurfaceGenerate(Operator):
    bl_idname = 'scene.tm_multi_surface_generate'
    bl_label = 'Generate'
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def execute(self, context):
        scene = context.scene
        settings = scene.trackmania_surface_settings
        borders = scene.trackmania_multi_surface.borders
        materials = scene.trackmania_multi_surface.materials
        
        simplify_threshold = radians(scene.trackmania_multi_surface.simplify_threshold)
        
        eps = 0.001
        
        count = 0
        min_index = 100
        stdout_dump = io.StringIO()
        
        material_count = len(materials)
        border_count = len(borders)
        max_count = material_count * pow(border_count, 4)
        
        raw_vertices = 0
        raw_edges = 0
        raw_polygons = 0
        simplified_vertices = 0
        simplified_edges = 0
        simplified_polygons = 0
        
        scene_name = scene.name
        
        for m in range(len(materials)):
            material = materials[m]
            if material.material is None:
                continue
            
            material_name = material.export_name if material.export_name else material.material.name
            settings.top_material = material.material
            base_path = scene_name + '/' + material_name + '/'
            
            index0 = 100
            prev0 = -1
            for c0 in range(len(borders)):
                index1= 100
                prev1 = -1
                for c1 in range(len(borders)):
                    index2 = 100
                    for c2 in range(len(borders)):
                        for c3 in range(len(borders)):
                            current_count = m*pow(border_count,4)+c0*pow(border_count,3)+c1*pow(border_count, 2)+c2*border_count+c3
                            print('{}/{} ({}%)'.format(current_count, max_count, round(current_count/max_count*100)))
                            curve0 = borders[c0].curve
                            curve1 = borders[c1].curve
                            curve2 = borders[c2].curve
                            curve3 = borders[c3].curve
                            
                            b0 = border.Border.from_curve(curve0, borders[c0].flip)
                            b1 = border.Border.from_curve(curve1, borders[c1].flip)
                            b2 = border.Border.from_curve(curve2, borders[c2].flip)
                            b3 = border.Border.from_curve(curve3, borders[c3].flip)
                            
                            if abs(b0.length - b2.length) > eps or abs(b1.length - b3.length) > eps:
                                continue

                            z1 = 00 + b0.height
                            z2 = z1 + b1.height
                            z3 = z2 + b2.height
                            z0 = z3 + b3.height
                            if z1 < -eps or z2 < -eps or z3 < -eps or (z3 <= eps and (z1 > eps or z2 > eps)) or abs(z0) > eps:
                                continue
                            
                            if z3 < eps and (z1 > eps or z2 > eps):
                                continue
                            
                            if prev0 != c0:
                                index0 -= 1
                                index1 = 99
                                index2 = 99
                            elif prev1 != c1:
                                index1 -= 1
                                index2 = 99
                            else:
                                index2 -= 1
                            prev0 = c0
                            prev1 = c1
                            
                            if index0 < min_index:
                                min_index = index0
                            if index1 < min_index:
                                min_index = index1
                            if index2 < min_index:
                                min_index = index2
                            
                            name = base_path + '{}-{}{}/{}-{}{}/{}-{}-{}-{}{}-{}{}-{}{}-{}{}'.format(
                                index0,
                                curve0.name, 'f' if borders[c0].flip else '',
                                index1,
                                curve1.name, 'f' if borders[c1].flip else '',
                                index2,
                                scene_name,
                                material_name,
                                curve0.name, 'f' if borders[c0].flip else '',
                                curve1.name, 'f' if borders[c1].flip else '',
                                curve2.name, 'f' if borders[c2].flip else '',
                                curve3.name, 'f' if borders[c3].flip else ''
                            )
                            scene.trackmania_item.export_path = name
                            
                            settings.border_0.curve = curve0
                            settings.border_0.flip = borders[c0].flip
                            settings.border_2.curve = curve1
                            settings.border_2.flip = borders[c1].flip
                            settings.border_1.curve = curve2
                            settings.border_1.flip = not borders[c2].flip
                            settings.border_3.curve = curve3
                            settings.border_3.flip = not borders[c3].flip
                            print('Generating and exporting: {}'.format(name))
                            
                            with redirect_stdout(stdout_dump):
                                bpy.ops.scene.tm_surface_update()
                                
                                # Simplify mesh
                                raw_vertices += len(settings.surface.data.vertices)
                                raw_edges += len(settings.surface.data.edges)
                                raw_polygons += len(settings.surface.data.polygons)
                                '''
                                settings.surface.select_set(True)
                                context.view_layer.objects.active = settings.surface
                                bpy.ops.object.mode_set(mode='EDIT')
                                bpy.ops.mesh.select_mode(type='VERT')
                                bpy.ops.mesh.select_all(action='SELECT')
                                bpy.ops.mesh.dissolve_limited(angle_limit=simplify_threshold, use_dissolve_boundaries=True)
                                bpy.ops.object.mode_set(mode='OBJECT')
                                '''
                                simplified_vertices += len(settings.surface.data.vertices)
                                simplified_edges += len(settings.surface.data.edges)
                                simplified_polygons += len(settings.surface.data.polygons)
                                
                                bpy.ops.trackmania.export()
                                
                            count += 1

        print('Generated {} surface items.'.format(count))
        print('Max node per folder was {}'.format(100 - min_index))
        print('Generated/Exported vertices: {}/{} (saved {}%)'.format(simplified_vertices, raw_vertices,
            round((raw_vertices - simplified_vertices) * 100 / raw_vertices)))
        print('Generated/Exported edges: {}/{} (saved {}%)'.format(simplified_edges, raw_edges,
            round((raw_edges - simplified_edges) * 100 / raw_edges)))
        print('Generated/Exported polygons: {}/{} (saved {}%)'.format(simplified_polygons, raw_polygons,
            round((raw_polygons - simplified_polygons) * 100 / raw_polygons)))
        return {'FINISHED'}

# Panels

class VIEW3D_OT_UpdateActiveSurface(Operator):
    bl_idname = 'scene.tm_surface_update'
    bl_label = 'Update'
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def execute(self, context):
        fail_reason = generate_surface(context)
        
        if fail_reason is not None:
            self.report({'ERROR'}, fail_reason)
            return {'CANCELLED'}
        return {'FINISHED'}

class VIEW3D_PT_TM_Surface(Panel):
    bl_idname = 'VIEW3D_PT_TM_Surface'
    bl_label = 'Surface'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def draw(self, context):
        pass

class VIEW3D_PT_TM_MultiSurface(Panel):
    bl_parent_id = VIEW3D_PT_TM_Surface.bl_idname
    bl_idname = 'VIEW3D_PT_TM_MultiSurface'
    bl_label = 'Multi Surface'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.trackmania_multi_surface
        
        # Borders
        layout.label(text='Borders:')
        row = layout.row()
        row.template_list('VIEW3D_UL_MultiSurfaceBorderItems', '', settings, 'borders', settings, 'selected_border', rows=4)
        
        col = row.column(align=True)
        col.operator(VIEW3D_OT_MultiSurfaceBordersEdit.bl_idname, text='+').action = 'ADD'
        col.operator(VIEW3D_OT_MultiSurfaceBordersEdit.bl_idname, text='-').action = 'REMOVE'
        col.separator()
        col.operator(VIEW3D_OT_MultiSurfaceBordersEdit.bl_idname, icon='TRIA_UP', text='').action = 'UP'
        col.operator(VIEW3D_OT_MultiSurfaceBordersEdit.bl_idname, icon='TRIA_DOWN', text='').action = 'DOWN'
        
        # Materials
        layout.label(text='Top Materials:')
        row = layout.row()
        row.template_list('VIEW3D_UL_MultiSurfaceMaterialItems', '', settings, 'materials', settings, 'selected_material', rows=4)
        
        col = row.column(align=True)
        col.operator(VIEW3D_OT_MultiSurfaceMaterialsEdit.bl_idname, text='+').action = 'ADD'
        col.operator(VIEW3D_OT_MultiSurfaceMaterialsEdit.bl_idname, text='-').action = 'REMOVE'
        col.separator()
        col.operator(VIEW3D_OT_MultiSurfaceMaterialsEdit.bl_idname, icon='TRIA_UP', text='').action = 'UP'
        col.operator(VIEW3D_OT_MultiSurfaceMaterialsEdit.bl_idname, icon='TRIA_DOWN', text='').action = 'DOWN'
        
        layout.prop(settings, 'simplify_threshold')
        
        layout.operator(VIEW3D_OT_MultiSurfaceGenerate.bl_idname)

class VIEW3D_PT_TM_ActiveSurface(Panel):
    bl_parent_id = VIEW3D_PT_TM_Surface.bl_idname
    bl_idname = 'VIEW3D_PT_TM_ActiveSurface'
    bl_label = 'Active'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == 'OBJECT'
    
    def draw_common_settings(self, layout, settings):
        common = layout.column()
        
        header = common.row()
        header.alignment = 'CENTER'
        header.label(text='Common')
        
        body = common.column(align=True)
        body.prop(settings, 'enable_continuous_update')
        body.prop(settings, 'bezier_precision')
        body.prop(settings, 'grid_subdivisions_flat')
        body.prop(settings, 'grid_subdivisions_curved')
        body.prop(settings, 'height')
        body.prop(settings, 'lightmap_margin')
        
        body.prop(settings, 'top_material')
        body.prop(settings, 'bottom_material')
        body.prop(settings, 'side_material')
    
    def draw_screw(self, layout, settings):
        screw = layout.column()
        
        header = screw.row()
        header.alignment = 'CENTER'
        header.label(text='Screw')
        
        body = screw.column(align=True)
        draw_border(body, settings.border_0, 'Border')
    
    def draw_connector(self, layout, settings):
        connector = layout.column()
        
        header = connector.row()
        header.alignment = 'CENTER'
        header.label(text='Connector')
        
        body = connector.column(align=True)
        draw_border(body, settings.border_0, 'East Border')
        draw_border(body, settings.border_1, 'West Border')
        draw_border(body, settings.border_2, 'North Border')
        draw_border(body, settings.border_3, 'South Border')
        
        row = body.row()
        row.prop(settings, 'preserve_tangents')
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.trackmania_surface_settings
        
        layout.prop(settings, 'surface_type')
        
        if settings.surface_type != 'NONE':
            self.draw_common_settings(layout, settings)
        
        if settings.surface_type == 'SCREW':
            self.draw_screw(layout, settings)
        elif settings.surface_type == 'CONNECTOR':
            self.draw_connector(layout, settings)
        
        if settings.surface_type != 'NONE':
            layout.operator(VIEW3D_OT_UpdateActiveSurface.bl_idname)
            

classes = (
    SCENE_PG_BorderSettings,
    SCENE_PG_MultiSurfaceMaterial,
    SCENE_PG_SurfaceSettings,
    SCENE_PG_MultiSurfaceSettings,
    VIEW3D_OT_MultiSurfaceBordersEdit,
    VIEW3D_OT_MultiSurfaceMaterialsEdit,
    VIEW3D_OT_MultiSurfaceGenerate,
    VIEW3D_UL_MultiSurfaceBorderItems,
    VIEW3D_UL_MultiSurfaceMaterialItems,
    VIEW3D_OT_UpdateActiveSurface,
    VIEW3D_PT_TM_Surface,
    VIEW3D_PT_TM_MultiSurface,
    VIEW3D_PT_TM_ActiveSurface
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.trackmania_surface_settings = PointerProperty(type=SCENE_PG_SurfaceSettings)
    bpy.types.Scene.trackmania_multi_surface = PointerProperty(type=SCENE_PG_MultiSurfaceSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.trackmania_surface_settings
    del bpy.types.Scene.trackmania_multi_surface
