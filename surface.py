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
''' Will be used later
class ANY_PG_MaterialListItem(PropertyGroup):
    bl_idname = 'ANY_PG_MaterialListItem'
    
    @property
    def name(self):
        return self.data.name
    
    data: PointerProperty(type=Material)

class ANY_PG_MaterialList(PropertyGroup):
    bl_idname = 'ANY_PG_MaterialList'

    list: CollectionProperty(
        name='List',
        type=ANY_PG_MaterialListItem
    )
    
    selection_index: IntProperty(
        name='Selection Index'
    )
    
    def add_new_to_list(self, context):
        if not self.new_item is None:
            self.selection_index = len(self.list)
            new_item = self.list.add()
            new_item.data = self.new
            self.new = None
    
    new: PointerProperty(
        type=Material,
        name='New Material',
        update=add_new_to_list
    )
'''
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

def generate_surface_screw(object):
    settings = object.trackmania_surface_settings
    print('generating screw surface')
    pass

def generate_surface_connector(object):
    settings = object.trackmania_surface_settings
    
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
        
        vertices.extend([Vector((
            east_point.x,
            blend_factor * north_point.x + (1 - blend_factor) * south_point.x,
            blend_factor * north_point.y + (1 - blend_factor) * south_point.y
        )) for north_point, south_point in zip(north_points_cpy, south_points_cpy)])
        
        if i != 0:
            n = len(north_points)
            faces.extend([((i - 1) * n + j, i * n + j, i * n + j + 1, (i - 1) * n + j + 1) for j in range(n - 1)])
    
    # Offset Z so lowest corner at 0
    z_corners = [0, east_border.size.y, east_border.size.y + north_border.size.y, south_border.size.y]
    offset = Vector((0, 0, -min(z_corners)))
    for vertice in vertices: vertice += offset
    
    # Replace current object mesh
    mesh = bpy.data.meshes.new('Surface')
    mesh.from_pydata(vertices, [], faces)
    if not settings.material is None:
        mesh.materials.append(settings.material)
    old_mesh = object.data
    object.data = mesh
    bpy.data.meshes.remove(old_mesh)
    
    # Set UV layers
    uv_base_material = mesh.uv_layers.new(name='BaseMaterial')
    mesh.uv_layers.active = uv_base_material
    for face in mesh.polygons:
        for vertex_id, loop_id in zip(face.vertices, face.loop_indices):
            vertex = mesh.vertices[vertex_id]
            uv_base_material.data[loop_id].uv = (vertex.co[0] / 32, vertex.co[1] / 32)
    mesh.uv_layers.new(name='Lightmap')
    

def generate_surface(object):
    settings = object.trackmania_surface_settings
    
    if settings.surface_type == 'SCREW':
        return generate_surface_screw(object)
    elif settings.surface_type == 'CONNECTOR':
        return generate_surface_connector(object)
    
    return 'Surface type is None'

class OBJECT_PG_SurfaceSettings(PropertyGroup):
    bl_idname = 'OBJECT_PG_CommonSurfaceSettings'
    
    def __init__(self):
        super().__init__()
        for _ in range(4):
            self.borders.add()
    
    def update(self, context):
        if self.enable_continuous_update:
            generate_surface(self.id_data)
       
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
    
    bezier_precision: IntProperty(
        name='Bezier Precision',
        description='How many time bezier curved is sambled before surface is projected on it',
        min=0,
        soft_max=256,
        default=128,
        update=update
    )
    
    material: PointerProperty(
        type=Material,
        name='Material',
        description='Material of generated surface',
        update=update
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
    
    def execute(self, context):
        surface_obj = context.active_object
        fail_reason = generate_surface(surface_obj)
        
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
        return not context.active_object is None and context.active_object.type == 'MESH'
    
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
        return not context.active_object is None and context.active_object.type == 'MESH'
    
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
        body.prop(settings, 'material')
    
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
