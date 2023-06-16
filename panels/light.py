import bpy
from bpy.types import Panel


class LIGHT_PT_TrackmaniaLight(Panel):
    bl_idname = 'LIGHT_PT_TrackmaniaLight'
    bl_label = 'Trackmania Light'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'LIGHT'
    
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

def register():
    bpy.utils.register_class(LIGHT_PT_TrackmaniaLight)

def unregister():
    bpy.utils.unregister_class(LIGHT_PT_TrackmaniaLight)
