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
    IntProperty,
    PointerProperty,
    StringProperty
)
from mathutils import Vector
from random import random

from . import border

# HACK reload
import importlib
border = importlib.reload(border)

# Properties
class OBJECT_PG_BorderSettings(PropertyGroup):
    bl_idname = 'OBJECT_PG_BorderSettings'
    
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

def generate_surface_screw(context, object):
    settings = object.trackmania_surface_settings
    print('generating screw surface')
    pass

def create_pivot(context, name):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'PLAIN_AXES'
    obj.trackmania_pivot.is_pivot = True
    context.scene.collection.objects.link(obj)
    return obj
    

def generate_surface_connector(context, object):
    settings = object.trackmania_surface_settings
    
    # East border
    print('East border')
    if settings.border_0.curve is None:
        return 'East border is not set'
    if not border.is_valid_curve(settings.border_0.curve):
        return 'East border is invalid'
    east_border = border.Border.from_curve(settings.border_0.curve, settings.border_0.flip)
    
    # West border
    print('West border')
    if settings.border_1.curve is None:
        return 'West border is not set'
    if not border.is_valid_curve(settings.border_1.curve):
        return 'West border is invalid'
    west_border = border.Border.from_curve(settings.border_1.curve, settings.border_1.flip)
    
    # East & West points
    print('East & West points')
    east_west_subdivisions = settings.grid_subdivisions_flat if (east_border.is_flat and west_border.is_flat) else settings.grid_subdivisions_curved
    east_points = east_border.sample(east_west_subdivisions, settings.bezier_precision)
    west_points = west_border.sample(east_west_subdivisions, settings.bezier_precision)
    m = len(east_points)
    
    # North border
    print('North border')
    if settings.border_2.curve is None:
        return 'North border is not set'
    if not border.is_valid_curve(settings.border_2.curve):
        return 'North border is invalid'
    north_border = border.Border.from_curve(settings.border_2.curve, settings.border_2.flip)
    
    # South border
    print('South border')
    if settings.border_3.curve is None:
        return 'South border is not set'
    if not border.is_valid_curve(settings.border_3.curve):
        return 'South border is invalid'
    south_border = border.Border.from_curve(settings.border_3.curve, settings.border_3.flip)
    
    # North & South points
    print('North & South points')
    north_south_subdivisions = settings.grid_subdivisions_flat if (north_border.is_flat and south_border.is_flat) else settings.grid_subdivisions_curved
    north_points = north_border.sample(north_south_subdivisions, settings.bezier_precision)
    south_points = south_border.sample(north_south_subdivisions, settings.bezier_precision)
    n = len(north_points)

    
    # Validate borders join
    print('Validate border join')
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
    print('Blend borders')
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
            faces.append(((i-1)*n*2+n-1,i*n*2+n-1,i*n*2+n+n-1,(i-1)*n*2+n+n-1))
        
        if i == len(east_points) - 1:
            faces.extend([(i*n*2+j, i*n*2+j+n, i*n*2+j+n+1, i*n*2+j+1) for j in range(n - 1)])
    
    # Offset Z so lowest corner at 0
    print('Offset Z')
    z_corners = [0, east_border.size.y, east_border.size.y + north_border.size.y, south_border.size.y]
    offset = Vector((0, 0, -min(z_corners)))
    for vertice in vertices: vertice += offset
    
    # Replace current object mesh
    print('Replace mesh')
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
    print('Set Base Material UV')
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
                z = 0
                if vertex_id % 2 == 0:
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
    
    # Set Lightmap's UV
    print('Set Lightmap UV')
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
            for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
                vertex = mesh.vertices[vertex_id]
                x = margin + (vertex.co[0] / east_border.length) * (0.5 - 2 * margin)
                y = margin + (vertex.co[1] / north_border.length) * (0.5 - 2 * margin)
                uv_lightmap.data[loop_id].uv = (x, y)
        elif (f - (n - 1)) % (2 * (n - 1) + 2) < 2 * (n - 1): # Bottom face
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
    

def generate_surface(context, object):
    settings = object.trackmania_surface_settings
    
    if settings.surface_type == 'SCREW':
        return generate_surface_screw(context, object)
    elif settings.surface_type == 'CONNECTOR':
        return generate_surface_connector(context, object)
    
    return 'Surface type is None'

class OBJECT_PG_SurfaceSettings(PropertyGroup):
    bl_idname = 'OBJECT_PG_SurfaceSettings'
    
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
        default=1,
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
        type=OBJECT_PG_BorderSettings,
        name='Border 0',
        description='Border 0 of generated surface',
        update=update
    )
    
    border_1: PointerProperty(
        type=OBJECT_PG_BorderSettings,
        name='Border 1',
        description='Border 1 of generated surface',
        update=update
    )
    
    border_2: PointerProperty(
        type=OBJECT_PG_BorderSettings,
        name='Border 2',
        description='Border 2 of generated surface',
        update=update
    )
    
    border_3: PointerProperty(
        type=OBJECT_PG_BorderSettings,
        name='Border 3',
        description='Border 3 of generated surface',
        update=update
    )
    
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




# Panels

class VIEW3D_OT_UpdateActiveSurface(Operator):
    bl_idname = 'trackmania_surface.update_active'
    bl_label = 'Update'
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.object.mode == 'OBJECT'
    
    def execute(self, context):
        object = context.active_object
        fail_reason = generate_surface(context, object)
        
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
        return context.active_object is not None and context.active_object.type == 'MESH' and context.object.mode == 'OBJECT'
    
    def draw(self, context):
        pass

class VIEW3D_PT_TM_ActiveSurface(Panel):
    bl_parent_id = VIEW3D_PT_TM_Surface.bl_idname
    bl_idname = 'VIEW3D_PT_TM_ActiveSurface'
    bl_label = 'Active'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.object.mode == 'OBJECT'
    
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
        settings = context.active_object.trackmania_surface_settings
        
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
    OBJECT_PG_BorderSettings,
    OBJECT_PG_SurfaceSettings,
    VIEW3D_OT_UpdateActiveSurface,
    VIEW3D_PT_TM_Surface,
    VIEW3D_PT_TM_ActiveSurface
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.trackmania_surface_settings = PointerProperty(type=OBJECT_PG_SurfaceSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.trackmania_surface_settings
