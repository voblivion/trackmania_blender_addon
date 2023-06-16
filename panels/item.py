import bpy
from bpy.types import Panel


class COLLECTION_PT_TrackmaniaItem(Panel):
    bl_idname = 'COLLECTION_PT_TrackmaniaItem'
    bl_label = 'Trackmania Item'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    bl_context = 'collection'
    
    @classmethod
    def poll(cls, context):
        return context.collection is not None
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        category = layout.box()
        category.label(text='Levitation')
        category.prop(item_settings, 'ghost_mode')
        category.prop(item_settings, 'fly_step')
        category.prop(item_settings, 'fly_offset')
        
        category = layout.box()
        category.label(text='Grid')
        category.prop(item_settings, 'grid_horizontal_step')
        category.prop(item_settings, 'grid_horizontal_offset')
        category.prop(item_settings, 'grid_vertical_step')
        category.prop(item_settings, 'grid_vertical_offset')
        
        category = layout.box()
        category.label(text='Pivot')
        category.prop(item_settings, 'pivot_manual_switch')
        category.prop(item_settings, 'pivot_automatic_snap')
        if not item_settings.pivot_automatic_snap:
            category.prop(item_settings, 'pivot_snap_distance')
        
        category = layout.box()
        category.label(text='Other')
        category.prop(item_settings, 'scale')
        category.prop(item_settings, 'waypoint_type')
        category.prop(item_settings, 'not_on_item')
        category.prop(item_settings, 'one_axis_rotation')
        category.prop(item_settings, 'auto_rotation')
        
        category = layout.box()
        category.label(text='Icon')
        category.prop(item_settings, 'icon_generate')
        if item_settings.icon_generate:
            category.prop(item_settings, 'icon_enable_camera')
            if item_settings.icon_enable_camera:
                category.prop(item_settings, 'icon_camera_pitch')
                category.prop(item_settings, 'icon_camera_yaw')
            category.prop(item_settings, 'icon_enable_sun')
            if item_settings.icon_enable_sun:
                category.prop(item_settings, 'icon_sun_color')
                category.prop(item_settings, 'icon_sun_offset_pitch')
                category.prop(item_settings, 'icon_sun_offset_yaw')

def register():
    bpy.utils.register_class(COLLECTION_PT_TrackmaniaItem)

def unregister():
    bpy.utils.unregister_class(COLLECTION_PT_TrackmaniaItem)
