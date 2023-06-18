import bpy
from bpy.types import Panel


class _SHARED_PT_TrackmaniaLight(Panel):
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.active_object in context.selected_objects and context.active_object.type == 'LIGHT'
    
    def draw(self, context):
        layout = self.layout
        light_object = context.active_object
        light = light_object.data
        
        layout.prop(light, 'type')
        if light.type not in ['POINT', 'SPOT']:
            category = layout.box()
            category.label(text='Warning: only \'Point\' and \'Spot\' lights can be exported.')
            return
        layout.prop(light, 'color')
        layout.prop(light, 'energy')
        layout.prop(light, 'distance')
        if light.type == 'SPOT':
            layout.prop(light, 'spot_size')
            layout.prop(light, 'spot_blend')

class PROPERTIES_PT_TrackmaniaLight(_SHARED_PT_TrackmaniaLight):
    bl_idname = 'PROPERTIES_PT_TrackmaniaLight'
    bl_label = 'Trackmania'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

class VIEW3D_PT_TrackmaniaLight(_SHARED_PT_TrackmaniaLight):
    bl_idname = 'VIEW3D_PT_TrackmaniaLight'
    bl_label = 'Light'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw_header(self, context):
        self.text = 'Light - ' + context.active_object.name
    
    def draw(self, context):
        self.text = 'Item - ' + context.active_object.name
        super().draw(context)
