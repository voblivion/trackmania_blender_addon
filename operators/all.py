import bpy
from . import (base, icon, item, mesh, mesh_params, nadeo_import,)

# HACK reload
import importlib
base = importlib.reload(base)


class SCENE_OT_TrackmaniaExportAll(base.SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_all'
    bl_label = 'Trackmania Export'
    bl_description = 'Exports mesh, icon, and necessary xml files then import to trackmania.'
    
    def export(self, context):
        
        success = False
        try:
            bpy.ops.trackmania.export_mesh()
            bpy.ops.trackmania.export_mesh_params()
            bpy.ops.trackmania.export_icon()
            bpy.ops.trackmania.export_item()
            bpy.ops.trackmania.nadeo_import()
            self.report({'INFO'}, 'Export succeeded.')
            success = True
        except Exception as e:
            self.report({'ERROR'}, 'Failed to export: {}'.format(e))
        
        return success
