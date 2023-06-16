import bpy
from bpy.types import Operator
import math
import mathutils
import pathlib
from ..utils import export

# HACK reload
import importlib
export = importlib.reload(export)


def _is_main_object(object):
    return object.trackmania_export.export_type in ['SEPARATE', 'UNIQUE']

class _SCENE_OT_TrackmaniaExportBase(Operator):
    bl_options = {'REGISTER'}
    
    def get_sub_path(self, context):
        objects = context.view_layer.objects.selected
        if not objects:
            self.report({'ERROR'}, 'No select object to export.')
            return None
        
        main_object = next((object for object in objects if _is_main_object(object)), None)
        
        collection = context.collection
        if collection is None:
            self.report({'ERROR'}, 'No collection active to get item settings from.')
            return None
        
        parent_collection = collection if main_object else export.get_parent_collection(collection)
        export_item = main_object if main_object else collection
        export_settings = export_item.trackmania_export
        
        sub_path = pathlib.Path(export_settings.get_export_path(export_item.name, parent_collection))
        
        return sub_path
        