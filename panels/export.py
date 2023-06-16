import bpy
from bpy.types import Panel


class _SHARED_PT_TrackmaniaExport(Panel):
    bl_label = 'Trackmania Export'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return (object in context.selected_objects and object.type in ['MESH', 'LIGHT', 'EMPTY']) or (object not in context.selected_objects and context.collection is not None)
    
    def draw(self, context):
        layout = self.layout
        export_settings = self.get_export_settings(context)
        
        layout.prop(export_settings, 'export_type')
        if export_settings.is_path_useful():
            layout.prop(export_settings, 'export_path_type')
            if export_settings.export_path_type == 'CUSTOM':
                layout.prop(export_settings, 'custom_export_path')

class OBJECT_PT_TrackmaniaExport(_SHARED_PT_TrackmaniaExport):
    bl_idname = 'MESH_PT_TrackmaniaExport'
    bl_context = 'object'
    
    def get_export_settings(self, context):
        return context.active_object.trackmania_export

class COLLECTION_PT_TrackmaniaExport(_SHARED_PT_TrackmaniaExport):
    bl_idname = 'COLLECTION_PT_TrackmaniaExport'
    bl_context = 'collection'
    
    def get_export_settings(self, context):
        return context.collection.trackmania_export

def register():
    bpy.utils.register_class(OBJECT_PT_TrackmaniaExport)
    bpy.utils.register_class(COLLECTION_PT_TrackmaniaExport)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_TrackmaniaExport)
    bpy.utils.unregister_class(COLLECTION_PT_TrackmaniaExport)
