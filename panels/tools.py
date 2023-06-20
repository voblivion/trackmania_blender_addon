import bpy
from bpy.types import Panel
from .. import operators

# HACK reload
import importlib
operators = importlib.reload(operators)


class VIEW3D_PT_TrackmaniaTools(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaTools'
    bl_label = 'Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout

class VIEW3D_PT_TrackmaniaToolsMaterials(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaToolsMaterials'
    bl_label = 'Material'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaTools'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator(operators.SCENE_OT_TrackmaniaImportDefaultMaterials.bl_idname)
        layout.prop(context.scene, 'custom_material')
        layout.operator(operators.SCENE_OT_TrackmaniaCreateCustomMaterial.bl_idname)
        layout.prop_search(context.scene, 'default_material', bpy.data, 'materials', text='Default Material')
        layout.operator(operators.SCENE_OT_TrackmaniaAddDefaultMaterial.bl_idname)

class VIEW3D_PT_TrackmaniaToolsUVs(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaToolsUVs'
    bl_label = 'UV'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaTools'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        op = row.operator(operators.SCENE_OT_SelectUVLayer.bl_idname, text='Select BaseMaterial Layer')
        op.layer_name='BaseMaterial'
        
        op = row.operator(operators.SCENE_OT_CreateUVLayer.bl_idname, text='Create BaseMaterial Layer')
        op.layer_name='BaseMaterial'
        
        row = layout.row()
        op = row.operator(operators.SCENE_OT_SelectUVLayer.bl_idname, text='Select Lightmap Layer')
        op.layer_name='Lightmap'
        
        op = row.operator(operators.SCENE_OT_CreateUVLayer.bl_idname, text='Create Lightmap Layer')
        op.layer_name='Lightmap'
        
        row = layout.row()
        row.operator(operators.SCENE_OT_TrackmaniaRemoveExtraUVLayers.bl_idname, text='Remove Extra Layers')
        row.operator(operators.SCENE_OT_TrackmaniaCreateMissingUVLayers.bl_idname, text='Create Missing Layers')

class VIEW3D_PT_TrackmaniaToolsItem(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaToolsItem'
    bl_label = 'Names'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    bl_parent_id = 'VIEW3D_PT_TrackmaniaTools'
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(context.scene, 'current_item_prefix', text='Current Prefix')
        layout.operator(operators.SCENE_OT_TrackmaniaPrefixItem.bl_idname, text='Rename With Prefix')
