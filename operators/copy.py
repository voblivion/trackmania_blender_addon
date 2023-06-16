import bpy
from bpy.types import Operator


def _collect_collections(objects):
    collections = set()
    
    for object in objects:
        for collection in object.users_collection:
            collections.add(collection)
    
    return collections

class _SCENE_OT_TrackmaniaCopyCollection(Operator):
    bl_options = {'REGISTER'}
    
    def get_source_and_targets(self, context):
        source_collection = context.collection
        if source_collection is None:
            self.report({'ERROR'}, 'No active collection to copy collection settings from.')
            return None, set()
        
        if not context.view_layer.objects.selected:
            self.report({'ERROR'}, 'No selected object to retrieve collections to copy collection settings to.')
            return None, set()
        
        target_collections = _collect_collections(context.view_layer.objects.selected)
        if source_collection in target_collections:
            target_collections.remove(source_collection)
        if not target_collections:
            self.report({'ERROR'}, 'Trying to copy collection settings from a collection to itself.')
            return None, set()
        
        return source_collection, target_collections

class SCENE_OT_TrackmaniaCopyCollectionItem(_SCENE_OT_TrackmaniaCopyCollection):
    bl_idname = 'trackmania.copy_collection_item'
    bl_label = 'Copy Active Collection Item Settings'
    
    def execute(self, context):
        source_collection, target_collections = self.get_source_and_targets(context)
        if source_collection is None or not target_collections:
            return {'CANCELLED'}
        
        item_settings = source_collection.trackmania_item
        for collection in target_collections:
            collection.trackmania_item.ghost_mode = item_settings.ghost_mode
            collection.trackmania_item.fly_step = item_settings.fly_step
            collection.trackmania_item.fly_offset = item_settings.fly_offset
            collection.trackmania_item.grid_horizontal_step = item_settings.grid_horizontal_step
            collection.trackmania_item.grid_horizontal_offset = item_settings.grid_horizontal_offset
            collection.trackmania_item.grid_vertical_step = item_settings.grid_vertical_step
            collection.trackmania_item.grid_vertical_offset = item_settings.grid_vertical_offset
            collection.trackmania_item.pivot_manual_switch = item_settings.pivot_manual_switch
            collection.trackmania_item.pivot_automatic_snap = item_settings.pivot_automatic_snap
            collection.trackmania_item.pivot_snap_distance = item_settings.pivot_snap_distance
            collection.trackmania_item.waypoint_type = item_settings.waypoint_type
            collection.trackmania_item.scale = item_settings.scale
            collection.trackmania_item.not_on_item = item_settings.not_on_item
            collection.trackmania_item.one_axis_rotation = item_settings.one_axis_rotation
            collection.trackmania_item.auto_rotation = item_settings.auto_rotation
            collection.trackmania_item.icon_generate = item_settings.icon_generate
            collection.trackmania_item.icon_enable_camera = item_settings.icon_enable_camera
            collection.trackmania_item.icon_camera_pitch = item_settings.icon_camera_pitch
            collection.trackmania_item.icon_camera_yaw = item_settings.icon_camera_yaw
            collection.trackmania_item.icon_enable_sun = item_settings.icon_enable_sun
            collection.trackmania_item.icon_sun_color = item_settings.icon_sun_color
            collection.trackmania_item.icon_sun_offset_pitch = item_settings.icon_sun_offset_pitch
            collection.trackmania_item.icon_sun_offset_yaw = item_settings.icon_sun_offset_yaw
        
        self.report({'INFO'}, str(len(target_collections)) + ' collection item settings updated.')
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaCopyCollectionExport(_SCENE_OT_TrackmaniaCopyCollection):
    bl_idname = 'trackmania.copy_collection_export'
    bl_label = 'Copy Active Collection Export Settings'
    
    def execute(self, context):
        source_collection, target_collections = self.get_source_and_targets(context)
        if source_collection is None or not target_collections:
            return {'CANCELLED'}
        
        export_settings = source_collection.trackmania_export
        for collection in target_collections:
            collection.trackmania_export.export_type = export_settings.export_type
            collection.trackmania_export.export_path_type = export_settings.export_path_type
            collection.trackmania_export.custom_export_path = export_settings.custom_export_path
        
        self.report({'INFO'}, str(len(target_collections)) + ' collection export settings updated.')
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaCopyObjectExport(Operator):
    bl_idname = 'trackmania.copy_object'
    bl_label = 'Copy Active Object Export Settings'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        source_object = context.view_layer.objects.active
        if source_object is None:
            self.report({'ERROR'}, 'No active object to copy object settings from.')
            return {'CANCELLED'}
        
        if not context.view_layer.objects.selected:
            self.report({'ERROR'}, 'No selected object to copy object settings to.')
            return {'CANCELLED'}
        
        target_objects = set(context.view_layer.objects.selected)
        if source_object in target_objects:
            target_objects.remove(source_object)
        
        if not target_objects:
            self.report({'ERROR'}, 'Trying to copy object settings from an object to itself.')
            return {'CANCELLED'}
        
        export_settings = source_object.trackmania_export
        for object in target_objects:
            if export_settings.export_type in [item[0] for item in object.trackmania_export.get_export_types(object)]:
                object.trackmania_export.export_type = export_settings.export_type
            object.trackmania_export.export_path_type = export_settings.export_path_type
            object.trackmania_export.custom_export_path = export_settings.custom_export_path
        
        self.report({'INFO'}, str(len(target_objects)) + ' object export settings updated.')
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaCopyCollectionItem)
    bpy.utils.register_class(SCENE_OT_TrackmaniaCopyCollectionExport)
    bpy.utils.register_class(SCENE_OT_TrackmaniaCopyObjectExport)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaCopyCollectionItem)
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaCopyCollectionExport)
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaCopyObjectExport)
