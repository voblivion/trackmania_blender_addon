import bpy
import os

from math import radians
from mathutils import Matrix

from bpy.props import (
    BoolProperty,
    EnumProperty,
)

from bpy.types import (
    Menu,
    Operator,
    Panel,
)

def get_library(context):
    return context.blend_data.libraries.load(
        os.path.dirname(os.path.abspath(__file__)) + '/data.blend'
    )

library_spawn = None
def get_library_spawn(context):
    global library_spawn
    if library_spawn is None:
        with get_library(context) as (data_from, data_to):
            data_to.objects = ['Spawn']
        library_spawn = data_to.objects[0]
    return library_spawn

library_material_names = [
    'TMDebug_Trigger',
    'TM_PlatformTech',
    'TM_PlatformDirt',
    'TM_PlatformIce',
    'TM_PlatformGrass',
    'TM_DecoGrass',
    'TM_DecoSand',
    'TM_DecoSnow',
    'TM_DecoGrassHill',
    'TM_DecoSandHill',
    'TM_DecoSnowHill',
    'TM_StadiumGrass',
    'TM_TrackTop',
    'TM_TrackWall',
    'TM_RoadTech',
    'TM_RoadDirt',
    'TM_RoadIce',
    'TM_RoadBump',
]
MATID_TMDebug_Trigger = 0
library_materials = None
def get_library_materials(context):
    global library_materials
    
    if library_materials is None:
        to_load_material_names = list(filter(
            lambda name: name not in context.blend_data.materials,
            library_material_names
        ))
        
        with get_library(context) as (data_from, data_to):
            data_to.materials = to_load_material_names
        library_materials = [context.blend_data.materials[name] for name in library_material_names]
    return library_materials

library_curve_names = [
    '00_01',
    '00_11',
    '00_21',
    '01_12',
    '02_11',
    '10_12',
    '11_11',
    '11_12',
    '12_11',
    '12_32',
    '20_11',
    '21_11',
    '21_32',
    '22_11',
    '22_21',
]
def get_standard_curves(context):
    to_load_curve_names = list(filter(
        lambda name: name not in context.blend_data.curves,
        library_curve_names
    ))
    
    with get_library(context) as (data_from, data_to):
        data_to.curves = to_load_curve_names
    

class OBJECT_OT_TrackmaniaAddItem(Operator):
    bl_idname = 'object.trackmania_add_item'
    bl_label = 'Add Item (Scene)'
    bl_description = 'Creates an Item that can be exported to Trackmania'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.scene.new(type='NEW')
        
        scene = context.scene
        default_render_world = context.blend_data.worlds.get('TMDebug_DefaultRenderWorld')
        if default_render_world is None:
            default_render_world = context.blend_data.worlds.new('TMDebug_DefaultRenderWorld')
            color = 0x444444
        
        scene.world = default_render_world
        
        return {'FINISHED'}

class OBJECT_OT_TrackmaniaAddMesh(Operator):
    bl_idname = 'object.trackmania_add_mesh'
    bl_label = 'Add Mesh'
    bl_description = 'Creates a Mesh (or Trigger) to active item (scene)'
    bl_options = {'REGISTER', 'UNDO'}
    
    is_trigger: BoolProperty(default=False)
    
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        obj.name = 'Trigger' if self.is_trigger else 'Mesh'
        obj.data.trackmania_mesh.type = 'TRIGGER' if self.is_trigger else 'MESH'
        
        if self.is_trigger:
            mat = get_library_materials(context)[MATID_TMDebug_Trigger]
            obj.data.materials.append(mat)
        
        return {'FINISHED'}

class OBJECT_OT_TrackmaniaAddSpawn(Operator):
    bl_idname = 'object.trackmania_add_spawn'
    bl_label = 'Add Spawn point'
    bl_description = 'Adds a Spawn point to active item (scene)'
    bl_options = {'REGISTER', 'UNDO'}
    
    is_trigger: BoolProperty(default=False)
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        obj = context.blend_data.objects.new('Spawn Point', get_library_spawn(context).data)
        context.collection.objects.link(obj)
        obj.matrix_world = Matrix.Rotation(radians(90), 4, 'Z') @ Matrix.Rotation(radians(90), 4, 'X')
        obj.data.trackmania_mesh.type = 'SPAWN'
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}

class OBJECT_OT_TrackmaniaAddLight(Operator):
    bl_idname = 'object.trackmania_add_light'
    bl_label = 'Add Light'
    bl_description = 'Adds a Light to active item (scene)'
    bl_options = {'REGISTER', 'UNDO'}
    
    type: EnumProperty(items=(('POINT', 'Point', ''), ('SPOT', 'Spot', '')))
    
    def execute(self, context):
        bpy.ops.object.add(type='LIGHT')
        obj = context.active_object
        obj.data.type = self.type
        obj.name = 'Spot Light' if self.type == 'SPOT' else 'Point Light'
        obj.data.trackmania_light.export = True
        return {'FINISHED'}

class OBJECT_OT_TrackmaniaAddPivot(Operator):
    bl_idname = 'object.trackmania_add_pivot'
    bl_label = 'Add Pivot'
    bl_description = 'Adds a Pivot to active item (scene)'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.add(type='EMPTY')
        obj = context.active_object
        obj.name = 'Pivot'
        obj.empty_display_type = 'PLAIN_AXES'
        obj.trackmania_pivot.is_pivot = True
        return {'FINISHED'}

class MATERIAL_OT_TrackmaniaLoadMaterials(Operator):
    bl_idname = 'object.trackmania_load_materials'
    bl_label = 'Load Material Library'
    bl_description = 'Force-load default materials'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        get_library_materials(context)
        return {'FINISHED'}

class CURVE_OT_TrackmaniaLoadCurves(Operator):
    bl_idname = 'object.trackmania_load_curves'
    bl_label = 'Load Standard Curves'
    bl_description = 'Copies standard curves into active scene'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        get_standard_curves(context)
        return {'FINISHED'}

class VIEW3D_PT_TrackmanialLibrary(Panel):
    bl_idname = 'VIEW3D_PT_TrackmanialLibrary'
    bl_label = 'Material Library'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        self.layout.operator(MATERIAL_OT_TrackmaniaLoadMaterials.bl_idname)
        self.layout.operator(CURVE_OT_TrackmaniaLoadCurves.bl_idname)

class VIEW3D_MT_TrackmaniaAdd(Menu):
    bl_idname = 'VIEW3D_MT_TrackmaniaAdd'
    bl_label = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_TrackmaniaAddItem.bl_idname)
        layout.operator(OBJECT_OT_TrackmaniaAddPivot.bl_idname)
        layout.separator()
        layout.operator(OBJECT_OT_TrackmaniaAddMesh.bl_idname)
        layout.operator(OBJECT_OT_TrackmaniaAddMesh.bl_idname, text='Add Trigger').is_trigger = True
        layout.operator(OBJECT_OT_TrackmaniaAddSpawn.bl_idname)
        layout.separator()
        layout.operator(OBJECT_OT_TrackmaniaAddLight.bl_idname, text='Add Point Light')
        layout.operator(OBJECT_OT_TrackmaniaAddLight.bl_idname, text='Add Spot Light').type = 'SPOT'

def add_trackmania_add_menu(self, context):
    self.layout.menu(VIEW3D_MT_TrackmaniaAdd.bl_idname)

classes = (
    OBJECT_OT_TrackmaniaAddItem,
    OBJECT_OT_TrackmaniaAddMesh,
    OBJECT_OT_TrackmaniaAddSpawn,
    OBJECT_OT_TrackmaniaAddLight,
    OBJECT_OT_TrackmaniaAddPivot,
    VIEW3D_MT_TrackmaniaAdd,
    MATERIAL_OT_TrackmaniaLoadMaterials,
    CURVE_OT_TrackmaniaLoadCurves,
    VIEW3D_PT_TrackmanialLibrary,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.append(add_trackmania_add_menu)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(add_trackmania_add_menu)
    
    library_materials = None

