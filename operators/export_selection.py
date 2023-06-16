import bpy
from bpy.types import Operator
from ..utils import export
from . import (icon, item, mesh, mesh_params, nadeo_import)

def _find_layer_collection(layer_collection, collection):
    if layer_collection.collection is collection:
        return layer_collection
    
    for sub_layer_collection in layer_collection.children:
        found_layer_collection = _find_layer_collection(sub_layer_collection, collection)
        if found_layer_collection is not None:
            return found_layer_collection
    
    return None

def _set_active_collection(context, collection):
    if collection is None:
        context.view_layer.active_layer_collection = context.view_layer.layer_collection
        return
    
    layer_collection = _find_layer_collection(context.view_layer.active_layer_collection, collection)
    if layer_collection is None:
        context.view_layer.active_layer_collection = context.view_layer.layer_collection
        return
        
    context.view_layer.active_layer_collection = layer_collection

class SCENE_OT_TrackmaniaExportSelection(Operator):
    bl_idname = 'trackmania.export_selection'
    bl_label = 'Export Selection'
    bl_options = {'REGISTER'}
    bl_description = 'Every selected objects and every collection they belong to will be considered. All exportable items (Unique/Separate objects and non-empty non-None-export collections) will be imported into Trackmania.'
    
    def exports(self, context, main_object, collection, sub_objects):
        # 2> Select objects
        for sub_object in sub_objects:
            sub_object.select_set(True)
        context.view_layer.objects.active = main_object
        _set_active_collection(context, collection)
        
        # Exports
        succeeded = False
        try:
            bpy.ops.trackmania.export_mesh()
            bpy.ops.trackmania.export_mesh_params()
            if collection.trackmania_item.icon_generate:
                bpy.ops.trackmania.export_icon()
            bpy.ops.trackmania.export_item()
            bpy.ops.trackmania.nadeo_import()
            succeeded = True
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        # 2< Unselect objects
        _set_active_collection(context, None)
        context.view_layer.objects.active = None
        for sub_object in sub_objects:
            sub_object.select_set(False)
        
        return succeeded
    
    def execute(self, context):
        exportable_items = export.collect_exportable_items(context)
        
        # 1> Save objects select/active states
        old_collection = context.collection
        old_active_object = context.view_layer.objects.active
        old_selected_objects = [object for object in context.view_layer.objects.selected]
        for object in old_selected_objects:
            object.select_set(False)
        
        total_item_count = len(exportable_items['objects']) + len(exportable_items['collections'])
        succeeded_item_count = 0
        
        # Export object items
        for object in exportable_items['objects']:
            collection = next(iter(object.users_collection), None)
            if collection is None:
                continue
            sub_objects = export.collect_object_item_objects(context, object)
            
            if self.exports(context, object, collection, sub_objects):
                succeeded_item_count = succeeded_item_count + 1
        
        # Export collection items
        for collection in exportable_items['collections']:
            sub_objects = export.collect_collection_item_objects(context, collection)
            if not sub_objects:
                continue
            
            if self.exports(context, None, collection, sub_objects):
                succeeded_item_count = succeeded_item_count + 1
        
        # 1< Restore object select/active states
        _set_active_collection(context, old_collection)
        context.view_layer.objects.active = old_active_object
        for object in old_selected_objects:
            object.select_set(True)
        
        if succeeded_item_count != total_item_count:
            self.report({'ERROR'}, 'Only {} out of {} items successfully exported. Click to see details.'.format(succeeded_item_count, total_item_count))
        elif total_item_count == 1:
            self.report({'INFO'}, 'Item successfully exported.')
        else:
            self.report({'INFO'}, 'All {} items successfully exported.'.format(total_item_count))
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaExportSelection)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaExportSelection)
