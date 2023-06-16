import bpy
from . import export_operator_base
import os
import pathlib
import subprocess
from ..utils import export
from ..utils import preferences

# HACK reload
import importlib
export = importlib.reload(export)
export_operator_base = importlib.reload(export_operator_base)


class SCENE_OT_TrackmaniaNadeoImport(export_operator_base._SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.nadeo_import'
    bl_label = 'Nadeo Import'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        objects = context.view_layer.objects.selected
        collection = context.collection
        item_settings = collection.trackmania_item
        
        nadeo_importer_exe = str(pathlib.Path(preferences.get(context).install_dir, 'NadeoImporter.exe'))
        work_dir_path = export.get_work_dir_path(context)
        
        # Generate Path
        base_path = export.get_base_export_path(context)
        sub_path = self.get_sub_path(context)
        if sub_path is None:
            return {'CANCELLED'}
        path = base_path / sub_path
        relative_path = os.path.relpath(str(path) + '.Item.xml', work_dir_path)
        
        try:
            result = subprocess.check_output([nadeo_importer_exe, 'Item', relative_path])
            msg = result.decode('utf-8').split('\r\n', 1)[1].replace('\r', '')[:-1]
            self.report({'INFO'}, 'Item imported successfully: ' + msg)
        except Exception as e:
            msg = e.output.decode('utf-8').split('\r\n', 1)[1].replace('\r', '')[:-1]
            self.report({'ERROR_INVALID_CONTEXT'}, 'Error occured while importing item: ' + str(msg))
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaNadeoImport)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaNadeoImport)
