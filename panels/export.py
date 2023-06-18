import bpy
from bpy.types import Panel
from .. import operators

# HACK reload
import importlib
operators = importlib.reload(operators)


class VIEW3D_PT_TrackmaniaExport(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaExport'
    bl_label = 'Export'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(operators.SCENE_OT_TrackmaniaExportAll.bl_idname)
