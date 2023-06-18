import os
import pathlib
import subprocess
from . import base
from ..utils import preferences

# HACK reload
import importlib
base = importlib.reload(base)
preferences = importlib.reload(preferences)


class SCENE_OT_TrackmaniaNadeoImport(base.SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.nadeo_import'
    bl_label = 'Trackmania Nadeo Import'
    bl_description = 'Imports .Item.xml to Trackmania.'
    
    def export(self, context):
        objects = context.selected_objects
        item_settings = context.collection.trackmania_item
        path = base.SCENE_OT_TrackmaniaExportBase.get_item_path(context).with_suffix('.Item.xml')
        
        nadeo_importer_exe = str(pathlib.Path(preferences.get(context).install_dir, 'NadeoImporter.exe'))
        work_dir_path = pathlib.Path(preferences.get(context).user_dir) / 'Work'
        
        # Import
        success = False
        try:
            result = subprocess.check_output([nadeo_importer_exe, 'Item', os.path.relpath(str(path), work_dir_path)])
            msg = result.decode('utf-8').split('\r\n', 1)[1].replace('\r', '')[:-1]
            self.report({'INFO'}, 'Item imported successfully: ' + msg)
            success = True
        except Exception as e:
            msg = e.output.decode('utf-8').split('\r\n', 1)[1].replace('\r', '')[:-1]
            self.report({'ERROR'}, 'Error occured while importing item: ' + str(msg))
        
        return success
