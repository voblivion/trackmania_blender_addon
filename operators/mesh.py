import bpy
from . import export_operator_base
from ..utils import export

# HACK reload
import importlib
export = importlib.reload(export)
export_operator_base = importlib.reload(export_operator_base)


class SCENE_OT_TrackmaniaExportMesh(export_operator_base._SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_mesh'
    bl_label = 'Export Mesh'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        objects = context.view_layer.objects.selected
        collection = context.collection
        item_settings = collection.trackmania_item
        
        # Generate Path
        base_path = export.get_base_export_path(context)
        sub_path = self.get_sub_path(context)
        if sub_path is None:
            return {'CANCELLED'}
        path = base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
        
        # 1> Save/Update special objects names
        old_object_names = []
        old_socket_start = context.blend_data.objects.get('_socket_start')
        if old_socket_start is not None:
            old_socket_start.name = 'old_socket_start'
            old_object_names.append((old_socket_start, '_socket_start'))
        for object in objects:
            if object.type == 'MESH':
                old_object_names.append((object, object.name))
                object.name = object.data.trackmania_mesh.get_export_name(object.name)
        
        # 2> Save/Update window scene
        old_window_scene = context.window.scene
        context.window.scene = context.scene
        
        # Export
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            bpy.ops.export_scene.fbx(filepath=str(path) + '.fbx', object_types={'MESH', 'LIGHT'}, axis_up='Y', use_selection=True)
            self.report({'INFO'}, 'Mesh exported successfully: ' + str(path) + '.fbx.')
        except Exception as e:
            self.report({'ERROR'}, 'Error occured while exporting mesh: ' + str(e))
        
        # 2< Restore window scene
        context.window.scene = old_window_scene
        
        # 1< Restore special objects names
        for object_name in old_object_names:
            object_name[0].name = object_name[1]
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaExportMesh)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaExportMesh)
