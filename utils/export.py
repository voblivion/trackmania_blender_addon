import bpy
import pathlib
from . import preferences


collection_export_types = (
    ('COLLECTION', 'Collection', 'Collection is exported as its own item with every Collection objects inside of it.'),
    ('NONE', 'None', 'Collection is not exported into any item. Its objects can still be exported when setup to do so.'),
)

object_export_types = (
    ('COLLECTION', 'Collection', 'Object isn\'t exported as its own item but can be part of exported collection or separate objects.'),
    ('SEPARATE', 'Separate', 'Object is exported as its own item with any Collection object from the same collection.'),
    ('UNIQUE', 'Unique', 'Object is exported as its own item and with no other object.'),
    ('NONE', 'None', 'Object is not exported into any item.'),
)

pivot_export_types = (
    ('COLLECTION', 'Collection', 'Pivot isn\'t exported as its own item but can be part of exported collection or separate objects.'),
    ('NONE', 'None', 'Pivot is not exported into any item.'),
)

export_path_types = (
    ('HIERARCHY', 'Hierarchy', 'Collection/Object name becomes a filesystem node inside export folder of parent collection.'),
    ('PARENT', 'Parent', 'Similar to \'Hierarchy\' but this Collection is ignored and doesn\'t have its own folder.'),
    ('SIMPLE', 'Simple', 'Collection/Object name alone decides export paths. Slashes (\'/\') can be used in its name to create sub-folders.'),
    ('CUSTOM', 'Custom', 'User can provide desired path.')
)

def get_parent_collection(collection):
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
            return parent_collection
    return None

def get_work_dir_path(context):
    return pathlib.Path(preferences.get(context).user_dir) / 'Work'

def get_base_export_path(context):
    return get_work_dir_path(context) / 'Items'

def get_exportable_collection(collection):
    if collection is None:
        return None
    
    if collection.trackmania_export.export_type == 'COLLECTION':
        return collection
    
    return get_exportable_collection(get_parent_collection(collection))

def collect_exportable_items(context):
    objects = set()
    collections = set()
    
    for object in context.view_layer.objects.selected:
        if object.trackmania_export.export_type in ['SEPARATE', 'UNIQUE']:
            objects.add(object)
        
        if object.trackmania_export.export_type == 'COLLECTION' and object.type in ['MESH', 'LIGHT']:
            exportable_collection = get_exportable_collection(next(iter(object.users_collection), None))
            if exportable_collection is not None:
                collections.add(exportable_collection)
    
    return {
        'objects': objects,
        'collections': collections
    }

def collect_collection_item_objects(context, collection):
    return [object for object in collection.objects if object.trackmania_export.export_type == 'COLLECTION']

def collect_object_item_objects(context, object):
    collection = next(iter(object.users_collection), None)
    if collection is None or object.trackmania_export.export_type == 'UNIQUE':
        return [object]
    
    objects = collect_collection_item_objects(context, collection)
    objects.append(object)
    return objects
