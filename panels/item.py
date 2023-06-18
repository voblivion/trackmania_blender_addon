from bpy.types import Panel
from .. import operators

class VIEW3D_PT_TrackmaniaItem(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItem'
    bl_label = 'Item'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def get_export_name(self, context):
        return context.collection.name if context.collection.name != 'Scene Collection' else context.scene.name
    
    @classmethod
    def poll(cls, context):
        return not context.selected_objects
    
    def draw_header(self, context):
        self.text = 'Item - ' + self.get_export_name(context)
    
    def draw(self, context):
        self.text = 'Item - ' + self.get_export_name(context)
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        # TMP
        layout.operator(operators.SCENE_OT_TrackmaniaExportAll.bl_idname)
        
        row = layout.row()
        row.operator(operators.SCENE_OT_TrackmaniaItemCopy.bl_idname, icon='COPYDOWN')
        row.operator(operators.SCENE_OT_TrackmaniaItemPaste.bl_idname, icon='PASTEDOWN')
        layout.prop(item_settings, 'export_type')
        layout.prop(item_settings, 'creates_folder', icon='FILE_FOLDER')

class VIEW3D_PT_TrackmaniaItemLevitation(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemLevitation'
    bl_label = 'Levitation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaItem'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object in context.selected_objects:
            return False
        
        if context.collection.trackmania_item.export_type == 'NONE':
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        layout.prop(item_settings, 'ghost_mode', icon='GHOST_ENABLED')
        layout.prop(item_settings, 'fly_step')
        layout.prop(item_settings, 'fly_offset')

class VIEW3D_PT_TrackmaniaItemGrid(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemGrid'
    bl_label = 'Grid'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaItem'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object in context.selected_objects:
            return False
        
        if context.collection.trackmania_item.export_type == 'NONE':
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        layout.prop(item_settings, 'grid_horizontal_step')
        layout.prop(item_settings, 'grid_horizontal_offset')
        layout.prop(item_settings, 'grid_vertical_step')
        layout.prop(item_settings, 'grid_vertical_offset')

class VIEW3D_PT_TrackmaniaItemPivot(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemPivot'
    bl_label = 'Pivot'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaItem'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object in context.selected_objects:
            return False
        
        if context.collection.trackmania_item.export_type == 'NONE':
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        row = layout.row()
        row.prop(item_settings, 'pivot_manual_switch', icon='VIEW_PAN')
        row.prop(item_settings, 'pivot_automatic_snap', icon='SNAP_ON')
        if not item_settings.pivot_automatic_snap:
            layout.prop(item_settings, 'pivot_snap_distance')

class VIEW3D_PT_TrackmaniaItemMiscellaneous(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemMiscellaneous'
    bl_label = 'Miscellaneous'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaItem'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object in context.selected_objects:
            return False
        
        if context.collection.trackmania_item.export_type == 'NONE':
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        layout.prop(item_settings, 'scale')
        layout.prop(item_settings, 'waypoint_type')
        layout.prop(item_settings, 'not_on_item', icon='LOCKED')
        layout.prop(item_settings, 'one_axis_rotation', icon='AXIS_TOP')
        layout.prop(item_settings, 'auto_rotation', icon='ORIENTATION_GIMBAL')

class VIEW3D_PT_TrackmaniaItemIcon(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemIcon'
    bl_label = 'Icon'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaItem'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object in context.selected_objects:
            return False
        
        if context.collection.trackmania_item.export_type == 'NONE':
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.collection.trackmania_item
        
        row = layout.row()
        row.prop(item_settings, 'icon_generate_camera', icon='CAMERA_DATA')
        row.prop(item_settings, 'icon_generate_sun', icon='LIGHT_SUN')
        if item_settings.icon_generate_camera:
            layout.prop(item_settings, 'icon_camera_pitch')
            layout.prop(item_settings, 'icon_camera_yaw')
        if item_settings.icon_generate_sun:
            layout.prop(item_settings, 'icon_sun_color')
            layout.prop(item_settings, 'icon_sun_offset_pitch')
            layout.prop(item_settings, 'icon_sun_offset_yaw')


