import bpy
from bpy.types import (Operator,)
from bpy.props import (PointerProperty, StringProperty,)

class SCENE_OT_SelectUVLayer(Operator):
    bl_idname = 'uv.select_layer'
    bl_label = 'Select UV Layer'
    bl_description = 'Selects UV layer on selected items.'
    
    layer_name: StringProperty(name='layer_name')
    
    def execute(self, context):
        objects = context.selected_objects
        
        for object in objects:
            if object.type != 'MESH':
                continue
            
            mesh = object.data
            if self.layer_name in mesh.uv_layers:
                mesh.uv_layers[self.layer_name].active = True
        
        return {'FINISHED'}

class SCENE_OT_CreateUVLayer(Operator):
    bl_idname = 'uv.create_layer'
    bl_label = 'Create UV Layer'
    bl_description = 'Creates UV layer on selected items.'
    
    layer_name: StringProperty(name='layer_name')
    
    def execute(self, context):
        objects = context.selected_objects
        
        for object in objects:
            if object.type != 'MESH':
                continue
            
            mesh = object.data
            if self.layer_name not in mesh.uv_layers:
                mesh.uv_layers.new(name=self.layer_name)
                mesh.uv_layers[self.layer_name].active = True
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaAddDefaultMaterial(Operator):
    bl_idname = 'trackmania.add_default_material'
    bl_label = 'Add Default Material'
    bl_description = 'Adds a default material to selected objects without material.'
    
    def execute(self, context):
        objects = context.selected_objects
        
        material = bpy.data.materials[context.scene.selected_material] if context.scene.selected_material in bpy.data.materials else None
        if not material:
            material = bpy.data.materials.new(name='Default')
            material.trackmania_material.identifier = 'PlatformTech'
        
        modified_meshes_count = 0
        
        for object in objects:
            if object.type != 'MESH' or not object.data.trackmania_mesh.is_visible:
                continue
            
            mesh = object.data
            materials = [material for material in mesh.materials if material is not None]
            if not materials:
                self.report({'INFO'}, 'Material \'{}\' was added to mesh {}.'.format(material.name, object.name))
                mesh.materials.append(material)
                modified_meshes_count = modified_meshes_count + 1
        
        self.report({'INFO'}, '{} meshes were modified.'.format(modified_meshes_count))
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaCreateMissingUVLayers(Operator):
    bl_idname = 'trackmania.create_missing_uv_layers'
    bl_label = 'Create Missing UV Layers'
    bl_description = 'Creates UV layers necessary for mesh to be imported into Trackmania.'
    
    def execute(self, context):
        objects = context.selected_objects
        
        new_uv_layer_count = 0
        
        for object in objects:
            if object.type != 'MESH':
                continue
            
            mesh = object.data
            
            materials = [material for material in mesh.materials if material is not None]
            if not materials and mesh.trackmania_mesh.is_visible:
                self.report({'WARNING'}, 'Mesh {} is visible but has not materials. Cannot retrieve missing UV layers.')
                continue
            
            needs_base_material_uv = False
            needs_lightmap_uv = False
            for material in materials:
                needs_base_material_uv = needs_base_material_uv or material.trackmania_material.needs_base_material_uv
                needs_lightmap_uv = needs_lightmap_uv or material.trackmania_material.needs_lightmap_uv
            
            if needs_base_material_uv and 'BaseMaterial' not in mesh.uv_layers:
                mesh.uv_layers.new(name='BaseMaterial')
                self.report({'INFO'}, 'UV layer \'BaseMaterial\' was added to mesh {}.'.format(object.name))
                new_uv_layer_count = new_uv_layer_count + 1
            
            if needs_lightmap_uv and 'Lightmap' not in mesh.uv_layers:
                mesh.uv_layers.new(name='Lightmap')
                self.report({'INFO'}, 'UV layer \'Lightmap\' was added to mesh {}.'.format(object.name))
                new_uv_layer_count = new_uv_layer_count + 1
        
        self.report({'INFO'}, '{} UV layers were created.'.format(new_uv_layer_count))
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaRemoveExtraUVLayers(Operator):
    bl_idname = 'trackmania.remove_extra_uv_layers'
    bl_label = 'Remove Extra UV Layers'
    bl_description = 'Removes UV layers unnecessary for mesh to be imported into Trackmania.'
    
    def execute(self, context):
        objects = context.selected_objects
        
        removed_uv_layer_count = 0
        
        for object in objects:
            if object.type != 'MESH':
                continue
            
            mesh = object.data
            
            materials = [material for material in mesh.materials if material is not None]
            if not materials and mesh.trackmania_mesh.is_visible:
                self.report({'WARNING'}, 'Mesh {} is visible but has not materials. Cannot retrieve missing UV layers.')
                continue
            
            needs_base_material_uv = False
            needs_lightmap_uv = False
            for material in materials:
                needs_base_material_uv = needs_base_material_uv or material.trackmania_material.needs_base_material_uv
                needs_lightmap_uv = needs_lightmap_uv or material.trackmania_material.needs_lightmap_uv
            
            if not needs_base_material_uv and 'BaseMaterial' in mesh.uv_layers:
                mesh.uv_layers.remove(mesh.uv_layers['BaseMaterial'])
                self.report({'INFO'}, 'UV layer \'BaseMaterial\' was removed from mesh {}.'.format(object.name))
                removed_uv_layer_count = removed_uv_layer_count + 1
            
            if not needs_lightmap_uv and 'Lightmap' in mesh.uv_layers:
                mesh.uv_layers.remove(mesh.uv_layers['Lightmap'])
                removed_uv_layer_count = removed_uv_layer_count + 1
            
            for uv_layer in mesh.uv_layers:
                if uv_layer.name not in ['BaseMaterial', 'Lightmap']:
                    mesh.uv_layers.remove(uv_layer)
                    self.report({'INFO'}, 'UV layer \'{}\' was removed from mesh {}.'.format(uv_layer.name, object.name))
                    removed_uv_layer_count = removed_uv_layer_count + 1
        
        self.report({'INFO'}, '{} UV layers were removed.'.format(removed_uv_layer_count))
        
        return {'FINISHED'}


