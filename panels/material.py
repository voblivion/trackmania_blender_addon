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
        material_settings = context.material.trackmania_material
        
        layout.prop(material_settings, 'identifier')
        required_uv_layers = []
        if material_settings.needs_base_material_uv:
            required_uv_layers.append('BaseMaterial')
        if material_settings.needs_lightmap_uv:
            required_uv_layers.append('Liehgtmap')
        
        layout.label(text='Required UV layers: ' + ('None' if not required_uv_layers else ', '.join(required_uv_layers)))
        layout.prop(material_settings, 'physics')
        if material_settings.can_customize_gameplay:
            layout.prop(material_settings, 'gameplay')
        if material_settings.can_customize_color:
            layout.prop(material_settings, 'color')
