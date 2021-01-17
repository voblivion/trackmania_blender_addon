import bpy
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
)

class OBJECT_PG_TrackmaniaPivot(PropertyGroup):
    is_pivot: BoolProperty(
        name='Is Pivot',
        default=False
    )

class VIEW3D_PT_TrackmaniaPivot(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaPivot'
    bl_label = 'Pivot'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'EMPTY'
    
    def draw(self, context):
        layout = self.layout
        pivot_settings = context.active_object.trackmania_pivot
        
        layout.prop(pivot_settings, 'is_pivot')
    

class LIGHT_PG_TrackmaniaLight(PropertyGroup):
    export: BoolProperty(
        name='Export',
        default=False
    )

class VIEW3D_PT_TrackmaniaLight(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaLight'
    bl_label = 'Light'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'LIGHT'
    
    def draw(self, context):
        layout = self.layout
        light_settings = context.active_object.data.trackmania_light
        
        layout.prop(light_settings, 'export')

class MESH_PG_TrackmaniaMesh(PropertyGroup):
    bl_idname = 'MESH_PG_TrackmaniaMesh'
    
    type: EnumProperty(
        name='Type',
        items=(
            ('MESH', 'Mesh', 'A mesh be collidable and/or visible to player'),
            ('TRIGGER', 'Trigger', 'A trigger to be used by waypoint item'),
            ('SPAWN', 'Spawn', 'Waypoint spawn point'),
        )
    )
    
    is_visible: BoolProperty(
        name='Is Visible',
        default=True
    )
    
    is_collidable: BoolProperty(
        name='Is Collidable',
        default=True
    )
    
    @property
    def render_on_icon(self):
        return self.type == 'MESH' and self.is_visible
    
    def get_export_name(self, base_name):
        if self.type == 'SPAWN':
            return '_socket_start'
        elif self.type == 'TRIGGER':
            return '_trigger_' + base_name
        elif not self.is_visible and not self.is_collidable:
            return '_skip_' + base_name
        elif not self.is_visible:
            return '_notvisible_' + base_name
        elif not self.is_collidable:
            return '_notcollidable_' + base_name
        else:
            return base_name
    

class VIEW3D_PT_TrackmaniaMesh(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaMesh'
    bl_label = 'Mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        mesh_settings = context.active_object.data.trackmania_mesh
        
        layout.prop(mesh_settings, 'type')
        
        if mesh_settings.type == 'MESH':
            layout.prop(mesh_settings, 'is_visible')
            layout.prop(mesh_settings, 'is_collidable')
    

classes = (
    OBJECT_PG_TrackmaniaPivot,
    VIEW3D_PT_TrackmaniaPivot,
    MESH_PG_TrackmaniaMesh,
    VIEW3D_PT_TrackmaniaMesh,
    LIGHT_PG_TrackmaniaLight,
    VIEW3D_PT_TrackmaniaLight,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.trackmania_pivot = PointerProperty(type=OBJECT_PG_TrackmaniaPivot)
    bpy.types.Mesh.trackmania_mesh = PointerProperty(type=MESH_PG_TrackmaniaMesh)
    bpy.types.Light.trackmania_light = PointerProperty(type=LIGHT_PG_TrackmaniaLight)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.trackmania_pivot
    del bpy.types.Mesh.trackmania_mesh
    del bpy.types.Light.trackmania_light







