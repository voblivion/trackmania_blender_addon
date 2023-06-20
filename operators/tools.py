import bpy
from bpy.types import (Operator,)
from bpy.props import (PointerProperty, StringProperty,)
import re
import os

def _get_texture_dir():
    base = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(base, '..', 'textures'))
    return path

def _load_default_material_textures():
    path = _get_texture_dir() + '/default_material_textures.txt'
    file = open(path)
    lines = file.readlines()
    
    default_materials = []
    for line in lines:
        tokens = line[:-1].split(',')
        if len(tokens) < 2:
            continue
        default_materials.append((tokens[0], tokens[1]))
    return default_materials

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

def _init_material(material, image):
    material.use_nodes = True  
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # BSDF
    principled_bsdf = nodes.get('Principled BSDF')
    principled_bsdf.inputs['Specular'].default_value = 0
    principled_bsdf.inputs['Roughness'].default_value = 0.5
    
    # Trackmania texture
    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.image = image
    
    if material.trackmania_material.can_customize_color:
        # Texture HSV
        texture_hsv_node = nodes.new('ShaderNodeSeparateColor')
        texture_hsv_node.label = 'Texture HSV'
        texture_hsv_node.mode = 'HSV'
        links.new(texture_node.outputs[0], texture_hsv_node.inputs[0])
        
        # Color HSV
        color_hsv_node = nodes.new('ShaderNodeSeparateColor')
        color_hsv_node.label = 'Color HSV'
        color_hsv_node.mode = 'HSV'
        color_hsv_curves = color_hsv_node.inputs[0].driver_add('default_value')
        for channel in range(0, 3):
            driver = color_hsv_curves[channel].driver
            driver.type = 'SCRIPTED'
            driver.expression = 'value'
            variable = driver.variables.new()
            variable.name = 'value'
            target = variable.targets[0]
            target.id_type = 'MATERIAL'
            target.id = material
            target.data_path = 'trackmania_material.color[' + str(channel) + ']'
        
        # Combined S
        s_node = nodes.new('ShaderNodeMath')
        s_node.label = 'S'
        s_node.operation = 'MULTIPLY'
        links.new(texture_hsv_node.outputs[1], s_node.inputs[0])
        links.new(color_hsv_node.outputs[1], s_node.inputs[1])
        
        # Combined V
        v_node = nodes.new('ShaderNodeMath')
        v_node.label = 'V'
        v_node.operation = 'MULTIPLY'
        links.new(texture_hsv_node.outputs[2], v_node.inputs[0])
        links.new(color_hsv_node.outputs[2], v_node.inputs[1])
        
        # Combined RGB
        combined_color_node = nodes.new('ShaderNodeCombineColor')
        combined_color_node.label = 'Combined Color'
        combined_color_node.mode = 'HSV'
        links.new(color_hsv_node.outputs[0], combined_color_node.inputs[0])
        links.new(s_node.outputs[0], combined_color_node.inputs[1])
        links.new(v_node.outputs[0], combined_color_node.inputs[2])
        
        links.new(combined_color_node.outputs[0], principled_bsdf.inputs['Base Color'])
    else:
        links.new(texture_node.outputs[0], principled_bsdf.inputs['Base Color'])

class SCENE_OT_TrackmaniaImportDefaultMaterials(Operator):
    bl_idname = 'trackmania.import_default_materials'
    bl_label = 'Import Default Materials'
    bl_description = 'Imports default materials to be used for mesh-modeling.'
    
    def execute(self, context):
        default_material_textures = _load_default_material_textures()
        material_import_count = 0
        for default_material_texture in default_material_textures:
            material_name = default_material_texture[0]
            
            if material_name in bpy.data.materials:
                continue
            
            texture_name = default_material_texture[1]
            image = bpy.data.images.load(_get_texture_dir() + '\\' + texture_name, check_existing=True)
            material = bpy.data.materials.new(name=material_name)
            material.trackmania_material.identifier = material_name
            _init_material(material, image)
            
            material_import_count = material_import_count + 1
            
        self.report({'INFO'}, '{} materials imported.'.format(material_import_count))
        return {'FINISHED'}

class SCENE_OT_TrackmaniaCreateCustomMaterial(Operator):
    bl_idname = 'trackmania.create_custom_material'
    bl_label = 'Create Custom Material'
    bl_description = 'Creates a custom material whose color can be modified and visualized within blender.'
    
    def execute(self, context):
        material_name = context.scene.custom_material
        material_textures = _load_default_material_textures()
        texture_name = next((mt[1] for mt in material_textures if mt[0] == material_name), None)
        if texture_name is None:
            self.report({'ERROR'}, 'Invalid custom material \'{}\''.format(material_name))
            return {'CANCELLED'}
        
        image = bpy.data.images.load(_get_texture_dir() + '\\' + texture_name, check_existing=True)
        material = bpy.data.materials.new(name='Custom Material')
        material.trackmania_material.identifier = material_name
        _init_material(material, image)
        
        self.report({'INFO'}, 'Material \'{}\' successfuly created.'.format(material.name))
        return {'FINISHED'}
    

class SCENE_OT_TrackmaniaAddDefaultMaterial(Operator):
    bl_idname = 'trackmania.add_default_material'
    bl_label = 'Add Default Material To Objects'
    bl_description = 'Adds a default material to selected objects which do not have any material.'
    
    def execute(self, context):
        objects = context.selected_objects
        
        material = bpy.data.materials[context.scene.default_material] if context.scene.default_material in bpy.data.materials else None
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



class SCENE_OT_TrackmaniaPrefixItem(Operator):
    bl_idname = 'trackmania.prefix_rename'
    bl_label = 'Add Prefix'
    bl_description = 'Adds current ordering prefix to active element (object or collection) and decrements it for future uses.'
    
    def execute(self, context):
        element = context.collection if context.active_object not in context.selected_objects else context.active_object
        
        match = re.search(r'^Z\d+-(.*)$', element.name)
        name = match.group(1) if match else element.name
        
        element.name = 'Z' + str(context.scene.current_item_prefix) + '-' + name
        context.scene.current_item_prefix = context.scene.current_item_prefix - 1
        
        return {'FINISHED'}

