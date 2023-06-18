import bpy
from bpy.types import Panel


class _SHARED_PT_TrackmaniaMesh(Panel):
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object in context.selected_objects and context.active_object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        mesh_settings = context.active_object.data.trackmania_mesh
        
        layout.prop(mesh_settings, 'mesh_type')
        
        if mesh_settings.mesh_type == 'MESH':
            row = layout.row()
            row.prop(mesh_settings, 'is_visible', icon='HIDE_OFF')
            row.prop(mesh_settings, 'is_collidable', icon='MOD_PHYSICS')

class PROPERTIES_PT_TrackmaniaMesh(_SHARED_PT_TrackmaniaMesh):
    bl_idname = 'PROPERTIES_PT_TrackmaniaMesh'
    bl_label = 'Trackmania Mesh'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

class VIEW3D_PT_TrackmaniaMesh(_SHARED_PT_TrackmaniaMesh):
    bl_idname = 'VIEW3D_PT_TrackmaniaMesh'
    bl_label = 'Mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw_header(self, context):
        self.text = 'Mesh - ' + context.active_object.name
    
    def draw(self, context):
        self.text = 'Mesh - ' + context.active_object.name
        super().draw(context)
