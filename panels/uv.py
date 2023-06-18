import bpy
from bpy.types import Panel
from .. import operators

# HACK reload
import importlib
operators = importlib.reload(operators)


class VIEW3D_PT_TrackmaniaMaterials(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaMaterials'
    bl_label = 'Materials'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop_search(context.scene, 'selected_material', bpy.data, 'materials', text='Default Material')
        layout.operator(operators.SCENE_OT_TrackmaniaAddDefaultMaterial.bl_idname)
        
        op = layout.operator(operators.SCENE_OT_SelectUVLayer.bl_idname, text='Select Lightmap UV Layer')
        op.layer_name='Lightmap'
        
        op = layout.operator(operators.SCENE_OT_SelectUVLayer.bl_idname, text='Select BaseMaterial UV Layer')
        op.layer_name='BaseMaterial'
        
        op = layout.operator(operators.SCENE_OT_CreateUVLayer.bl_idname, text='Create Lightmap UV Layer')
        op.layer_name='Lightmap'
        
        op = layout.operator(operators.SCENE_OT_CreateUVLayer.bl_idname, text='Create BaseMaterial UV Layer')
        op.layer_name='BaseMaterial'
        
        layout.operator(operators.SCENE_OT_TrackmaniaCreateMissingUVLayers.bl_idname)
        layout.operator(operators.SCENE_OT_TrackmaniaRemoveExtraUVLayers.bl_idname)
