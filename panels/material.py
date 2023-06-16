import bpy
from bpy.types import Panel
from ..utils import tm


class MATERIAL_PT_TrackmaniaMaterial(Panel):
    bl_idname = 'MATERIAL_PT_TrackmaniaMaterial'
    bl_label = 'Trackmania Material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    bl_context = 'material'
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def draw(self, context):
        layout = self.layout
        trackmania_settings = context.material.trackmania_material
        
        layout.prop(trackmania_settings, 'material')
        layout.prop(trackmania_settings, 'physics')
        if trackmania_settings.material in tm.gameplay_override_compatible_materials:
            layout.prop(trackmania_settings, 'gameplay')
        if tm.get_tm_materials(context)[trackmania_settings.material].allows_color:
            layout.prop(trackmania_settings, 'color')

def register():
    bpy.utils.register_class(MATERIAL_PT_TrackmaniaMaterial)

def unregister():
    bpy.utils.unregister_class(MATERIAL_PT_TrackmaniaMaterial)

