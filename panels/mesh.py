import bpy
from bpy.types import Panel


class MESH_PT_TrackmaniaMesh(Panel):
    bl_idname = 'MESH_PT_TrackmaniaMesh'
    bl_label = 'Trackmania Mesh'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        mesh_settings = context.active_object.data.trackmania_mesh
        
        layout.prop(mesh_settings, 'mesh_type')
        
        if mesh_settings.mesh_type == 'MESH':
            layout.prop(mesh_settings, 'is_visible')
            layout.prop(mesh_settings, 'is_collidable')

def register():
    bpy.utils.register_class(MESH_PT_TrackmaniaMesh)

def unregister():
    bpy.utils.unregister_class(MESH_PT_TrackmaniaMesh)
