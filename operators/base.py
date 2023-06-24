import bpy
from bpy.types import Operator
from bpy.props import (EnumProperty, StringProperty)
import pathlib
from ..utils import preferences

def _is_scene_collection(collection):
    return any([scene.collection is collection for scene in bpy.data.scenes])

def _get_scene(root_collection):
    return next((scene for scene in bpy.data.scenes if scene.collection is root_collection), None)

def _get_export_name(object_or_collection):
    scene = _get_scene(object_or_collection)
    if scene:
        return scene.name
    return object_or_collection.name

def _get_parent_collection(collection):
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
            return parent_collection
    for scene in bpy.data.scenes:
        if collection.name in scene.collection.children.keys():
            return scene.collection
    return None

def _get_item_settings(collection):
    if collection is None:
        return None
    
    if collection.trackmania_item.export_type == 'INHERIT':
        return _get_item_settings(_get_parent_collection(collection))
    
    return collection.trackmania_item
    
def _get_collection_items(objects):
    collections = set()
    for object in objects:
        for collection in object.users_collection:
            item_settings = _get_item_settings(collection)
            if item_settings and item_settings.export_type == 'SINGLE':
                collections.add(collection)
    items = []
    for collection in collections:
        items.append((
            collection,
            None,
            [object for object in collection.objects if object.type in ['EMPTY', 'MESH', 'LIGHT']]
        ))
    return items

def _get_object_items(objects):
    items = []
    for object in objects:
        if object.type not in ['MESH', 'LIGHT']:
            continue
        for collection in object.users_collection:
            item_settings = _get_item_settings(collection)
            if item_settings and item_settings.export_type == 'MULTIPLE':
                items.append((
                    collection,
                    object,
                    [pivot for pivot in collection.objects if pivot.type == 'EMPTY'] + [object]
                ))
    return items

# (collection, main_object, objects)
def _get_items(objects):
    return _get_collection_items(objects) + _get_object_items(objects)

def _get_collection_ancestry(collection):
    if collection is None:
        return []
    
    return _get_collection_ancestry(_get_parent_collection(collection)) + [collection]

def _to_path(ancestry):
    if not ancestry:
        return pathlib.Path()
    
    if not ancestry[-1].trackmania_item.creates_folder:
        return _to_path(ancestry[:-1])
    
    return _to_path(ancestry[:-1]) / _get_export_name(ancestry[-1])

class SCENE_OT_TrackmaniaExportBase(Operator):
    
    @staticmethod
    def get_item_path(context):
        base_folder = pathlib.Path(preferences.get(context).user_dir) / 'Work' / 'Items'

        path = base_folder / _to_path(_get_collection_ancestry(context.collection))
        item_settings = _get_item_settings(context.collection)
        if item_settings.export_type == 'MULTIPLE':
            if context.active_object is None:
                return None
            path = path / context.active_object.name
        
        return path
    
    def get_item_settings(self, context):
        return _get_item_settings(context.collection)
    
    def execute(self, context):
        items = _get_items(context.selected_objects)
        success = 0
        for item in items:
            override = context.copy()
            override['collection'] = item[0]
            override['active_object'] = item[1]
            override['selected_objects'] = item[2]
            with context.temp_override(**override):
                success = success + 1 if self.export(context) else success
        
        if len(items) > 1:
            self.report({'INFO'}, '{} out of {} items exported successfully.'.format(success, len(items)))
        
        return {'FINISHED'}
