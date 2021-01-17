import bpy
import os
import subprocess
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
)
from itertools import chain
from math import radians, sqrt, degrees
from mathutils import Vector, Matrix
from pathlib import Path
from xml.etree import ElementTree as et
import xml.dom.minidom

from . import bd_utils
import importlib
bd_utils = importlib.reload(bd_utils)

class SCENE_PG_TrackmaniaItem(PropertyGroup):
    bl_idname = 'SCENE_PG_TrackmaniaItem'
    
    export_mesh: BoolProperty(
        name='Mesh',
        description='If set, will export its mesh (fbx) when using export operations',
        default=True
    )
    
    export_mesh_params: BoolProperty(
        name='Mesh Params',
        description='If set, will export its mesh params (xml) when using export operations',
        default=True
    )
    
    export_icon: BoolProperty(
        name='Icon',
        description='If set, will export its icon (tga) when using export operations',
        default=True
    )
    
    export_item: BoolProperty(
        name='Item',
        description='If set, will export its item (xml) when using export operations',
        default=True
    )
    
    export_nadeo: BoolProperty(
        name='Nadeo Importer',
        description='If set, will execute Nadeo Importer after everything is exported',
        default=True
    )
    
    # Levitation
    ghost_mode: BoolProperty(
        name='Ghost Mode',
        description='Whether or not editor should ignore blocks/items when placing generated item or attempt to place it on them',
        default=False
    )
    fly_step: FloatProperty(
        name='Step',
        description='Increment by which cursor altitude is changed when scrolling with this item in hand',
        default=0
    )
    fly_offset: FloatProperty(
        name='Offset',
        description='Offset from virtual vertical grid defined by Fly Step',
        default=0
    )
    # Grid
    grid_horizontal_step: FloatProperty(
        name='Horizontal Step',
        description='Size of horizontal grid item can be placed on',
        default=0
    )
    grid_horizontal_offset: FloatProperty(
        name='Horizontal Offset',
        description='By how much item is offset when placed on its horizontal grid',
        default=0
    )
    grid_vertical_step: FloatProperty(
        name='Vertical Step',
        description='Size of vertical grid item can be placed on',
        default=0
    )
    grid_vertical_offset: FloatProperty(
        name='Vertical Offset',
        description='By how much item is offset when placed on its vertical grid',
        default=0
    )
    # Pivot
    pivot_manual_switch: BoolProperty(
        name='Manual Switch',
        description='Disables automatic pivot switch',
        default=False
    )
    pivot_automatic_snap: BoolProperty(
        name='Automatic Snap',
        description='Whether or not pivot snap distance is automatically decided by editor',
        default=True
    )
    pivot_snap_distance: FloatProperty(
        name='Snap Distance',
        description='Distance at which editor will try to snap item on another according to their pivot points',
        default=1,
        min=0
    )
    
    @property
    def pivot_snap_distance_raw(self):
        if self.pivot_automatic_snap:
            return -1
        return self.pivot_snap_distance
    
    # Other
    waypoint_type: EnumProperty(
        name='Waypoint Type',
        description='Type of waypoint, None if not a waypoint',
        items=(
            ('NONE', 'None', ''),
            ('Start', 'Start', ''),
            ('Finish', 'Finish', ''),
            ('StartFinish', 'Multilap', ''),
            ('Checkpoint', 'Checkpoint', ''),
        ),
    )
    scale: FloatProperty(
        name='Scale',
        description='Scale applied to object before import',
        default=1,
        min=0.01
    )
    not_on_item: BoolProperty(
        name='Not On Item',
        description='Prevents exported item from being placed on another item',
        default=False
    )
    one_axis_rotation: BoolProperty(
        name='One Axis Rotation',
        description='Only allows rotating object on its Yaw axis',
        default=False
    )
    auto_rotation: BoolProperty(
        name='Auto Rotation',
        description='Rotates item according to surface it is placed on',
        default=False
    )
    # Icon
    def update_camera_settings(self, context):
        bpy.ops.trackmania.render_icon(force_default_camera=True, save=False)
    
    icon_camera_pitch: FloatProperty(
        name='Camera Pitch',
        description='Pitch angle of default camera. Add your own camera to ignore.',
        default=45,
        update=update_camera_settings
    )
    icon_camera_yaw: FloatProperty(
        name='Camera Yaw',
        description='Yaw angle of camera. Add your own camera to ignore.',
        default=45,
        update=update_camera_settings
    )

def get_preferences(context):
    return context.preferences.addons['Trackmania'].preferences

def get_author_name(context):
    return get_preferences(context).author_name

def get_work_dir_path(context):
    return Path(get_preferences(context).user_dir) / 'Work'

def get_base_export_path(context):
    return get_work_dir_path(context) / 'Items'

class SCENE_OT_TrackmaniaRenderIcon(Operator):
    bl_idname = 'trackmania.render_icon'
    bl_label = 'Icon'
    bl_options = {'REGISTER'}
    
    force_default_camera: BoolProperty(name='Force Default Camera', default=False)
    save: BoolProperty(name='Save', default=True)
    
    @staticmethod
    def get_export_path(context):
        base_path = get_base_export_path(context)
        sub_path = Path(context.scene.name + '.tga')
        return base_path / sub_path.parents[0] / 'Icon' / sub_path.name
    
    def execute(self, context):
        scene = context.scene
        item_settings = scene.trackmania_item
        
        # Ensure scene render parameters are correct
        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = 'TARGA'
        
        # Set/Override camera if required
        custom_camera_object = scene.camera
        if True or custom_camera_object is None or self.force_default_camera:
            camera = bpy.data.cameras.new('Camera')
            camera.type = 'ORTHO'
            camera_object = bpy.data.objects.new('Camera', camera)
            context.collection.objects.link(camera_object)
            scene.camera = camera_object
            
            visible_objects = []
            for object in scene.objects:
                if not object.hide_render and object.type == 'MESH':
                    mesh_settings = object.data.trackmania_mesh
                    if mesh_settings.type == 'MESH' and mesh_settings.is_visible:
                        visible_objects.append(object)
            bounds_w = bd_utils.get_objects_bounds(visible_objects)
            center_position_w = bd_utils.get_vectors_center(bounds_w)
            center_matrix_w = Matrix.Translation(center_position_w)
            radius = max([bound.length for bound in bounds_w])
            camera_position_c = Matrix.Rotation(radians(item_settings.icon_camera_yaw), 4, 'Z') \
                @ Matrix.Rotation(radians(item_settings.icon_camera_pitch), 4, 'Y') \
                @ Vector((-1 - 2 * radius, 0, 0))
            camera_position_matrix_c = Matrix.Translation(camera_position_c)
            camera_look_at_matrix = (-camera_position_c).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            camera_matrix_w = center_matrix_w @ camera_position_matrix_c @ camera_look_at_matrix
            camera_object.matrix_world = camera_matrix_w
            
            item_matrix_v = bd_utils.inverse_matrix(camera_matrix_w)
            bounds_v = [item_matrix_v @ vector for vector in bounds_w]
            camera.ortho_scale = 2 * max(chain((abs(pos.x) for pos in bounds_v), (abs(pos.y) for pos in bounds_v)))
        
        # Set invisible in render objects that should be
        invisible_objects = []
        for object in scene.objects:
            if object.type == 'MESH' and not object.data.trackmania_mesh.render_on_icon:
                if not object.hide_render:
                    invisible_objects.append(object)
                    object.hide_render = True
                
        # Add light
        light = bpy.data.lights.new('Sun', type='SUN')
        light.energy = 3
        light_object = bpy.data.objects.new('Sun', light)
        scene.collection.objects.link(light_object)
        
        # Change render path
        export_path = self.get_export_path(context)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        prev_render_path = scene.render.filepath
        scene.render.filepath = str(export_path)
        
        bpy.ops.render.render(scene=scene.name, write_still=self.save)
        
        # Restore render path
        scene.render.filepath = prev_render_path
        
        # Remove light
        bpy.data.objects.remove(light_object)
        
        # Remove created camera and reset previous one
        if custom_camera_object is None or self.force_default_camera:
            bpy.data.objects.remove(scene.camera)
            if custom_camera_object is not None:
                scene.camera = custom_camera_object
        
        self.report({'INFO'}, 'Export {} done ({})'.format(self.bl_label, export_path))
        return {'FINISHED'}

class SCENE_OT_TrackmaniaExportMesh(Operator):
    bl_idname = 'trackmania.export_mesh'
    bl_label = 'Mesh'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context):
        base_path = get_base_export_path(context)
        sub_path = Path(context.scene.name + '.fbx')
        return base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
    
    def execute(self, context):
        scene = context.scene
        
        old_object_names = []
        prev_socket_start = context.blend_data.objects.get('_socket_start')
        if prev_socket_start is not None:
            prev_socket_start.name = '_socket_start.000'
            old_object_names.append((prev_socket_start, '_socket_start'))
        
        socket_start = None
        for object in scene.objects:
            if object.type == 'MESH':
                old_object_names.append((object, object.name))
                object.name = object.data.trackmania_mesh.get_export_name(object.name)
        
        export_path = self.get_export_path(context)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=str(export_path), object_types={'MESH', 'LIGHT'}, axis_up='Y')
        
        for entry in old_object_names:
            entry[0].name = entry[1]
        
        self.report({'INFO'}, 'Export {} done ({})'.format(self.bl_label, export_path))
        return {'FINISHED'}

class SCENE_OT_TrackmaniaExportMeshParams(Operator):
    bl_idname = 'trackmania.export_mesh_params'
    bl_label = 'Mesh Params'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context):
        base_path = get_base_export_path(context)
        sub_path = Path(context.scene.name + '.MeshParams.xml')
        return base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
    
    def execute(self, context):
        scene = context.scene
        item_settings = scene.trackmania_item
        
        export_path = self.get_export_path(context)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        mesh_export_path = SCENE_OT_TrackmaniaExportMesh.get_export_path(context)
        
        xml_mesh_params = et.Element('MeshParams')
        xml_mesh_params.set('MeshType', 'Static')
        xml_mesh_params.set('Collection', 'Stadium')
        xml_mesh_params.set('Scale', str(item_settings.scale))
        xml_mesh_params.set('FbxFile', os.path.relpath(mesh_export_path, export_path.parents[0]))
        
        xml_materials = et.SubElement(xml_mesh_params, 'Materials')
        materials = {}
        for object in scene.objects:
            for material_slot in object.material_slots:
                material = material_slot.material
                if material is not None:
                    materials[material.name] = material
        for material_name, material in materials.items():
            xml_material = et.SubElement(xml_materials, 'Material')
            xml_material.set('Name', material_name)
            xml_material.set('Link', material.trackmania_material.name)
            color = [int(channel * 255) for channel in material.trackmania_material.color]
            color = format((color[0] << 16) + (color[1] << 8) + color[2], 'x')
            xml_material.set('Color', color)
        
        file = open(str(export_path), 'w')
        file.write(xml.dom.minidom.parseString(et.tostring(xml_mesh_params)).toprettyxml())
        
        self.report({'INFO'}, 'Export {} done ({})'.format(self.bl_label, export_path))
        return {'FINISHED'}
    

class SCENE_OT_TrackmaniaExportItem(Operator):
    bl_idname = 'trackmania.export_item'
    bl_label = 'Item'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context):
        return get_base_export_path(context) / (context.scene.name + '.Item.xml')
    
    def execute(self, context):
        scene = context.scene
        item_settings = scene.trackmania_item
        
        export_path = self.get_export_path(context)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        mesh_params_export_path = SCENE_OT_TrackmaniaExportMeshParams.get_export_path(context)
        
        # Item
        xml_item = et.Element('Item')
        xml_item.set('Type', 'StaticObject')
        xml_item.set('Collection', 'Stadium')
        xml_item.set('AuthorName', get_author_name(context))
        
        # MeshParamsLink
        xml_mesh_params_link = et.SubElement(xml_item, 'MeshParamsLink')
        xml_mesh_params_link.set('File', os.path.relpath(mesh_params_export_path, export_path.parents[0]))
        
        # Waypoint
        if item_settings.waypoint_type != 'NONE':
            xml_waypoint = et.SubElement(xml_item, 'Waypoint')
            xml_waypoint.set('Type', item_settings.waypoint_type)
        
        # Pivots
        xml_pivots = et.SubElement(xml_item, 'Pivots')
        for object in scene.objects:
            if object.type == 'EMPTY':
                if object.trackmania_pivot.is_pivot:
                    xml_pivot = et.SubElement(xml_pivots, 'Pivot')
                    pos = object.location
                    xml_pivot.set('Pos', '{} {} {}'.format(pos.x, pos.z, pos.y))
        
        # PivotSnap
        if not item_settings.pivot_automatic_snap:
            xml_pivot_snap = et.SubElement(xml_item, 'PivotSnap')
            xml_pivot_snap.set('Distance', str(item_settings.pivot_snap_distance))
        
        # GridSnap
        xml_grid_snap = et.SubElement(xml_item, 'GridSnap')
        xml_grid_snap.set('HStep', str(item_settings.grid_horizontal_step))
        xml_grid_snap.set('HOffset', str(item_settings.grid_horizontal_offset))
        xml_grid_snap.set('VStep', str(item_settings.grid_vertical_step))
        xml_grid_snap.set('VOffset', str(item_settings.grid_vertical_offset))
        
        # Levitation
        xml_levitation = et.SubElement(xml_item, 'Levitation')
        xml_levitation.set('VStep', str(item_settings.fly_step))
        xml_levitation.set('VOffset', str(item_settings.fly_offset))
        xml_levitation.set('GhostMode', str(item_settings.ghost_mode).lower())
        
        # Options
        xml_options = et.SubElement(xml_item, 'Options')
        xml_options.set('ManualPivotSwitch', str(item_settings.pivot_manual_switch).lower())
        xml_options.set('OneAxisRotation', str(item_settings.one_axis_rotation).lower())
        xml_options.set('AutoRotation', str(item_settings.auto_rotation).lower())
        xml_options.set('NotOnItem', str(item_settings.not_on_item).lower())
    
        # Lights
        xml_lights = et.SubElement(xml_item, 'Lights')
        for object in scene.objects:
            if object.type == 'LIGHT' and object.data.type in ['POINT', 'SPOT']:
                light = object.data
                xml_light = et.SubElement(xml_lights, 'Light')
                color = [int(channel * 255) for channel in light.color]
                color = format((color[0] << 16) + (color[1] << 8) + color[2], 'x')
                xml_light.set('sRGB', color)
                xml_light.set('Name', object.name)
                xml_light.set('Intensity', str(light.energy))
                xml_light.set('Distance', str(light.distance))
                if light.type == 'POINT':
                    xml_light.set('Type', 'Point')
                else: # SPOT
                    xml_light.set('Type', 'Spot')
                    xml_light.set('SpotOuterAngle', str(degrees(light.spot_size)))
                    xml_light.set('SpotInnerAngle', str(sqrt(1-light.spot_blend) * degrees(light.spot_size)))
        
        file = open(str(export_path), 'w')
        file.write(xml.dom.minidom.parseString(et.tostring(xml_item)).toprettyxml())
        
        self.report({'INFO'}, 'Export {} done ({})'.format(self.bl_label, export_path))
        return {'FINISHED'}

class SCENE_OT_TrackmaniaNadeoImporter(Operator):
    bl_idname = 'trackmania.nadeo_importer'
    bl_label = 'Call Nadeo Importer'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        item_settings = scene.trackmania_item
        nadeo_importer_exe = str(Path(get_preferences(context).install_dir, 'NadeoImporter.exe'))
        work_dir_path = get_work_dir_path(context)
        item_path = str(SCENE_OT_TrackmaniaExportItem.get_export_path(context))
        relative_item_path = os.path.relpath(item_path, work_dir_path)
        process = subprocess.Popen([nadeo_importer_exe, 'Item', relative_item_path])
        print([nadeo_importer_exe, 'Item', relative_item_path])
        return {'FINISHED'}

class SCENE_OT_TrackmaniaExport(Operator):
    bl_idname = 'trackmania.export'
    bl_label = 'All'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        item_settings = context.scene.trackmania_item
        
        if item_settings.export_mesh:
            bpy.ops.trackmania.export_mesh()
        if item_settings.export_mesh_params:
            bpy.ops.trackmania.export_mesh_params()
        if item_settings.export_icon:
            bpy.ops.trackmania.render_icon(save=True)
        if item_settings.export_item:
            bpy.ops.trackmania.export_item()
        bpy.ops.trackmania.nadeo_importer()
        return {'FINISHED'}

class VIEW3D_PT_TrackmaniaItem(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItem'
    bl_label = 'Item'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.scene.trackmania_item
        
        category = layout.box()
        category.label(text='Levitation')
        category.prop(item_settings, 'ghost_mode')
        category.prop(item_settings, 'fly_step')
        category.prop(item_settings, 'fly_offset')
        
        category = layout.box()
        category.label(text='Grid')
        category.prop(item_settings, 'grid_horizontal_step')
        category.prop(item_settings, 'grid_horizontal_offset')
        category.prop(item_settings, 'grid_vertical_step')
        category.prop(item_settings, 'grid_vertical_offset')
        
        category = layout.box()
        category.label(text='Pivot')
        category.prop(item_settings, 'pivot_manual_switch')
        category.prop(item_settings, 'pivot_automatic_snap')
        if not item_settings.pivot_automatic_snap:
            category.prop(item_settings, 'pivot_snap_distance')
        
        category = layout.box()
        category.label(text='Other')
        category.prop(item_settings, 'scale')
        category.prop(item_settings, 'waypoint_type')
        category.prop(item_settings, 'not_on_item')
        category.prop(item_settings, 'one_axis_rotation')
        category.prop(item_settings, 'auto_rotation')
        
        category = layout.box()
        category.label(text='Icon')
        category.prop(item_settings, 'icon_camera_pitch')
        category.prop(item_settings, 'icon_camera_yaw')
        
        # TODO : export buttons
        category = layout.box()
        category.label(text='Export')
        row = category.row()
        row.prop(item_settings, 'export_mesh')
        row.prop(item_settings, 'export_mesh_params')
        row = category.row()
        row.prop(item_settings, 'export_icon')
        row.prop(item_settings, 'export_item')
        category.row().prop(item_settings, 'export_nadeo')
        
        row = category.row()
        row.operator(SCENE_OT_TrackmaniaExport.bl_idname, text='Current Scene/Item')
        row = category.row()
        row.operator(SCENE_OT_TrackmaniaExport.bl_idname, text='All Scenes/Items')





classes = (
    SCENE_PG_TrackmaniaItem,
    SCENE_OT_TrackmaniaExportMesh,
    SCENE_OT_TrackmaniaExportMeshParams,
    SCENE_OT_TrackmaniaRenderIcon,
    SCENE_OT_TrackmaniaExportItem,
    SCENE_OT_TrackmaniaNadeoImporter,
    SCENE_OT_TrackmaniaExport,
    VIEW3D_PT_TrackmaniaItem,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.trackmania_item = PointerProperty(type=SCENE_PG_TrackmaniaItem)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.trackmania_item


