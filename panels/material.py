import bpy
from bpy.types import Panel


class MATERIAL_PT_TrackmaniaMaterial(Panel):
    bl_idname = 'MATERIAL_PT_TrackmaniaMaterial'
    bl_label = 'Trackmania'
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
        
        layout.prop(trackmania_settings, 'identifier')
        layout.prop(trackmania_settings, 'physics')
        if trackmania_settings.can_customize_gameplay:
            layout.prop(trackmania_settings, 'gameplay')
        if trackmania_settings.can_customize_color:
            layout.prop(trackmania_settings, 'color')
