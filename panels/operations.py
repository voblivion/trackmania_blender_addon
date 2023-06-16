import bpy
from bpy.types import Panel
from ..operators import copy
from ..operators import export_selection

# HACK reload
import importlib
copy = importlib.reload(copy)
export_selection = importlib.reload(export_selection)



class VIEW3D_PT_TrackmaniaExportOperations(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaExportOperations'
    bl_label = 'Export Operations'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(export_selection.SCENE_OT_TrackmaniaExportSelection.bl_idname)

class VIEW3D_PT_TrackmaniaCopyOperations(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaCopyOperations'
    bl_label = 'Copy Operations'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(copy.SCENE_OT_TrackmaniaCopyCollectionItem.bl_idname)
        layout.operator(copy.SCENE_OT_TrackmaniaCopyCollectionExport.bl_idname)
        layout.operator(copy.SCENE_OT_TrackmaniaCopyObjectExport.bl_idname)

def register():
    bpy.utils.register_class(VIEW3D_PT_TrackmaniaExportOperations)
    bpy.utils.register_class(VIEW3D_PT_TrackmaniaCopyOperations)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_TrackmaniaExportOperations)
    bpy.utils.unregister_class(VIEW3D_PT_TrackmaniaCopyOperations)
