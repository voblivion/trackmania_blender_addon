import bpy
from bpy.types import (Panel, PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty)
import pathlib
from ..utils import export

# HACK reload
import importlib
export = importlib.reload(export)

class _SHARED_PG_TrackmaniaExport(PropertyGroup):
    def _get_export_types(self, context):
        return self.get_export_types(context.active_object)
    
    def get_export_path_types(self, context):
        if self.export_type != 'NONE':
            return (val for val in export.export_path_types if val[0] != 'PARENT')
        return export.export_path_types
    
    export_type: EnumProperty(
        name='Export Type',
        items=_get_export_types,
        default=0
    )
    
    export_path_type: EnumProperty(
        name='Path Type',
        items=get_export_path_types,
        default=0
    )
    
    custom_export_path: StringProperty(
        name='Custom Path'
    )
    
    def get_export_path(self, name, parent_collection):
        if self.export_path_type == 'SIMPLE':
            return name
        
        if self.export_path_type == 'CUSTOM':
            return pathlib.Path(self.custom_export_path)
        
        parent_path = pathlib.Path('')
        if parent_collection is not None:
            grand_parent_collection = export.get_parent_collection(parent_collection)
            parent_path = parent_collection.trackmania_export.get_export_path(parent_collection.name, grand_parent_collection)
        
        if self.export_path_type == 'PARENT':
            return parent_path
        
        return parent_path / name

class OBJECT_PG_TrackmaniaExport(_SHARED_PG_TrackmaniaExport):
    bl_idname = 'OBJECT_PG_TrackmaniaExport'
    
    def get_export_types(self, object):
        if object and object.type == 'EMPTY':
            return export.pivot_export_types
        return export.object_export_types
    
    def is_path_useful(self):
        return self.export_type != 'NONE'

class COLLECTION_PG_TrackmaniaExport(_SHARED_PG_TrackmaniaExport):
    bl_idname = 'COLLECTION_PG_TrackmaniaExport'
    
    def get_export_types(self, object):
        return export.collection_export_types
        
    def is_path_useful(self):
        return True

def register():
    bpy.utils.register_class(OBJECT_PG_TrackmaniaExport)
    bpy.utils.register_class(COLLECTION_PG_TrackmaniaExport)
    bpy.types.Object.trackmania_export = PointerProperty(type=OBJECT_PG_TrackmaniaExport)
    bpy.types.Collection.trackmania_export = PointerProperty(type=COLLECTION_PG_TrackmaniaExport)

def unregister():
    bpy.utils.unregister_class(OBJECT_PG_TrackmaniaExport)
    bpy.utils.unregister_class(COLLECTION_PG_TrackmaniaExport)
    del bpy.types.Object.trackmania_export
    del bpy.types.Collection.trackmania_export
