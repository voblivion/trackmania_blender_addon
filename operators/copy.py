from bpy.types import Operator

class SCENE_OT_TrackmaniaItemCopy(Operator):
    bl_idname = 'trackmania.item_copy'
    bl_label = 'Copy Item Settings'
    
    clipboard = None
    
    def execute(self, context):
        SCENE_OT_TrackmaniaItemCopy.clipboard = context.collection
        return {'FINISHED'}

class SCENE_OT_TrackmaniaItemPaste(Operator):
    bl_idname = 'trackmania.item_paste'
    bl_label = 'Paste Item Settings'
    
    copyable_properties = [
        'export_type', 'creates_folder', 'ghost_mode', 'fly_step', 'fly_offset',
        'grid_horizontal_step', 'grid_horizontal_offset', 'grid_vertical_step',
        'grid_vertical_offset', 'pivot_manual_switch', 'pivot_automatic_snap',
        'pivot_snap_distance', 'waypoint_type', 'scale', 'not_on_item', 'one_axis_rotation',
        'auto_rotation', 'icon_generate_camera', 'icon_camera_pitch', 'icon_camera_yaw',
        'icon_generate_sun', 'icon_sun_color', 'icon_sun_offset_pitch', 'icon_sun_offset_yaw',
    ]
    
    def execute(self, context):
        source = SCENE_OT_TrackmaniaItemCopy.clipboard
        
        if not source:
            self.report({'ERROR'}, 'Not copied item settings to paste.')
            return {'CANCELLED'}
        
        if source is context.collection:
            self.report({'WARNING'}, 'Attempting to paste item settings from same collection.')
            return {'CANCELLED'}
        
        for copyable_property in SCENE_OT_TrackmaniaItemPaste.copyable_properties:
            setattr(context.collection.trackmania_item, copyable_property, getattr(source.trackmania_item, copyable_property))
        
        self.report({'INFO'}, '"' + source.name + '" item settings copied to "' + context.collection.name + '".')
        return {'FINISHED'}
