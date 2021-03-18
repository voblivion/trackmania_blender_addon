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
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
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
    
    export_path: StringProperty(
        name='Export Path',
        description='Relative path (file included) it will be exported to',
        default='BlenderItem'
    )
    
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
    def update_icon_settings(self, context):
        bpy.ops.trackmania.render_icon(force_default_camera=True, save=False)
    
    icon_camera_pitch: FloatProperty(
        name='Camera Pitch',
        description='Pitch angle of default camera. Add your own camera to ignore.',
        default=45,
        update=update_icon_settings
    )
    icon_camera_yaw: FloatProperty(
        name='Camera Yaw',
        description='Yaw angle of camera. Add your own camera to ignore.',
        default=45,
        update=update_icon_settings
    )
    icon_enable_sun: BoolProperty(
        name='Enable Sun',
        description='If set, will add a sun to the scene before generating Item\'s Icon.',
        default=True,
        update=update_icon_settings
    )
    icon_sun_color: FloatVectorProperty(
        name='Sun Color',
        description='Color for generated Sun',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        default=(1, 1, 1),
        update=update_icon_settings
    )
    icon_sun_offset_pitch: FloatProperty(
        name='Sun Offset Pitch',
        description='By how much -relative to camera\'s pitch- sun\'s pitch is offset.',
        default=15,
        update=update_icon_settings
    )
    icon_sun_offset_yaw: FloatProperty(
        name='Sun Offset Yaw',
        description='By how much -relative to camera\'s yaw- sun\'s yaw is offset.',
        default=15,
        update=update_icon_settings
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
    def get_export_path(context, scene):
        base_path = get_base_export_path(context)
        sub_path = Path(scene.trackmania_item.export_path + '.tga')
        return base_path / sub_path.parents[0] / 'Icon' / sub_path.name
    
    scene: StringProperty(
        default=''
    )
    
    @staticmethod
    def offset_look_at(object, bounds_w, pitch, yaw):
        center_position_w = bd_utils.get_vectors_center(bounds_w)
        center_matrix_w = Matrix.Translation(center_position_w)
        radius = max([bound.length for bound in bounds_w])
        object_position_c = Matrix.Rotation(radians(yaw), 4, 'Z') \
            @ Matrix.Rotation(radians(pitch), 4, 'Y') \
            @ Vector((-1 - 2 * radius, 0, 0))
        object_position_matrix_c = Matrix.Translation(object_position_c)
        object_look_at_matrix = (-object_position_c).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        object_matrix_w = center_matrix_w @ object_position_matrix_c @ object_look_at_matrix
        object.matrix_world = object_matrix_w
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        item_settings = scene.trackmania_item
        
        # Ensure scene render parameters are correct
        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = 'TARGA'
        
        # Compute scene's bounds (for Camera and Sun placements)
        bounds_w = []
        if True:
            visible_objects = []
            for object in scene.objects:
                if not object.hide_render and object.type == 'MESH':
                    mesh_settings = object.data.trackmania_mesh
                    if mesh_settings.type == 'MESH' and mesh_settings.is_visible:
                        visible_objects.append(object)
            bounds_w = bd_utils.get_objects_bounds(visible_objects)
        
        # Set/Override camera if required
        custom_camera_object = scene.camera
        # TODO what about no default camera?
        if True or custom_camera_object is None or self.force_default_camera:
            camera = bpy.data.cameras.new('Camera')
            camera.type = 'ORTHO'
            camera_object = bpy.data.objects.new('Camera', camera)
            context.collection.objects.link(camera_object)
            scene.camera = camera_object
            
            self.offset_look_at(camera_object, bounds_w, item_settings.icon_camera_pitch, item_settings.icon_camera_yaw)
            item_matrix_v = bd_utils.inverse_matrix(camera_object.matrix_world)
            bounds_v = [item_matrix_v @ vector for vector in bounds_w]
            camera.ortho_scale = 2 * max(chain((abs(pos.x) for pos in bounds_v), (abs(pos.y) for pos in bounds_v)))
        
        # Set invisible in render objects that should be
        invisible_objects = []
        for object in scene.objects:
            if object.type == 'MESH' and not object.data.trackmania_mesh.render_on_icon:
                if not object.hide_render:
                    print(object)
                    invisible_objects.append(object)
                    object.hide_render = True
        
        # Add light
        sun_object = None
        if item_settings.icon_enable_sun:
            sun_light = bpy.data.lights.new('Sun', type='SUN')
            sun_light.energy = 3
            sun_light.color = item_settings.icon_sun_color
            sun_object = bpy.data.objects.new('Sun', sun_light)
            scene.collection.objects.link(sun_object)
            self.offset_look_at(
                sun_object,
                bounds_w,
                item_settings.icon_camera_pitch + item_settings.icon_sun_offset_pitch,
                item_settings.icon_camera_yaw + item_settings.icon_sun_offset_yaw
            )
        
        # Change render path
        export_path = self.get_export_path(context, scene)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        prev_render_path = scene.render.filepath
        scene.render.filepath = str(export_path)
        
        try:
            bpy.ops.render.render(scene=scene.name, write_still=self.save)
            self.report({'INFO'}, 'Icon render completed successfully.')
        except Exception as e:
            self.report({'ERROR', 'Unknown error while rendering Icon, check console for more info.'})
        
        # Restore render path
        scene.render.filepath = prev_render_path
        
        # Remove light
        if sun_object is not None:
            bpy.data.objects.remove(sun_object)
        
        # Reset previously hidden objects
        for object in invisible_objects:
            object.hide_render = False
        
        # Remove created camera and reset previous one
        if True or custom_camera_object is None or self.force_default_camera:
            bpy.data.objects.remove(scene.camera)
            if custom_camera_object is not None:
                scene.camera = custom_camera_object
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaExportMesh(Operator):
    bl_idname = 'trackmania.export_mesh'
    bl_label = 'Mesh'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context, scene):
        base_path = get_base_export_path(context)
        sub_path = Path(scene.trackmania_item.export_path + '.fbx')
        return base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
    
    scene: StringProperty(
        default=''
    )
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        
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
        
        start_mesh = None
        start_object = scene.objects.get('_socket_start')
        if start_object is not None:
            tmp_mesh = context.blend_data.meshes.new('__TMP__')
            start_mesh = start_object.data
            start_object.data = tmp_mesh
        
        export_path = self.get_export_path(context, scene)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        
        active_scene = context.scene
        context.window.scene = scene
        try:
            bpy.ops.export_scene.fbx(filepath=str(export_path), object_types={'MESH', 'LIGHT'}, axis_up='Y')
            context.window.scene = active_scene
            self.report({'INFO'}, 'Mesh export completed successfully.')
        except Exception as e:
            self.report({'ERROR', 'Unknown error while exporting Mesh, check console for more info.'})
        
        if start_object is not None:
            tmp_mesh = start_object.data
            start_object.data = start_mesh
            context.blend_data.meshes.remove(tmp_mesh)
        
        for entry in old_object_names:
            entry[0].name = entry[1]
        
        return {'FINISHED'}

def gamma_correct(channel):
    srgb = channel * 12.92 if channel < 0.0031308 else 1.055 * pow(channel, 1.0 / 2.4) - 0.055
    return max(min(int(srgb * 255 + 0.5), 255), 0)

def color_to_hex(color):
    rgb = [color.r, color.g, color.b]
    result = ''
    return '{:02X}{:02X}{:02X}'.format(gamma_correct(color.r), gamma_correct(color.g), gamma_correct(color.b))

class SCENE_OT_TrackmaniaExportMeshParams(Operator):
    bl_idname = 'trackmania.export_mesh_params'
    bl_label = 'Mesh Params'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context, scene):
        base_path = get_base_export_path(context)
        sub_path = Path(scene.trackmania_item.export_path + '.MeshParams.xml')
        return base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
    
    scene: StringProperty(
        default=''
    )
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        item_settings = scene.trackmania_item
        
        export_path = self.get_export_path(context, scene)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        mesh_export_path = SCENE_OT_TrackmaniaExportMesh.get_export_path(context, scene)
        
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
            xml_material.set('Color', color_to_hex(material.trackmania_material.color))
        
        try:
            file = open(str(export_path), 'w')
            file.write(xml.dom.minidom.parseString(et.tostring(xml_mesh_params)).toprettyxml())
            self.report({'INFO'}, 'Mesh Params export completed successfully.\n{}'.format(export_path))
        except Exception as e:
            self.report({'ERROR', 'Unknown error while exporting Mesh Params, check console for more info.'})
        
        return {'FINISHED'}
    

class SCENE_OT_TrackmaniaExportItem(Operator):
    bl_idname = 'trackmania.export_item'
    bl_label = 'Item'
    bl_options = {'REGISTER'}
    
    @staticmethod
    def get_export_path(context, scene):
        return get_base_export_path(context) / (scene.trackmania_item.export_path + '.Item.xml')
    
    scene: StringProperty(
        default=''
    )
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        item_settings = scene.trackmania_item
        
        export_path = self.get_export_path(context, scene)
        export_path.parents[0].mkdir(parents=True, exist_ok=True)
        mesh_params_export_path = SCENE_OT_TrackmaniaExportMeshParams.get_export_path(context, scene)
        
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
                    xml_pivot.set('Pos', '{} {} {}'.format(pos.x, pos.z, -pos.y))
        
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
            if object.type == 'LIGHT' and object.data.type in ['POINT', 'SPOT'] and object.date.trackmania_light.export:
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
        
        try:
            file = open(str(export_path), 'w')
            file.write(xml.dom.minidom.parseString(et.tostring(xml_item)).toprettyxml())
            self.report({'INFO'}, 'Item Export completed successfully.')
        except Exception as e:
            self.report({'ERROR', 'Unknown error while exporting Item, check console for more info.'})
        
        return {'FINISHED'}

class SCENE_OT_TrackmaniaNadeoImporter(Operator):
    bl_idname = 'trackmania.nadeo_importer'
    bl_label = 'Call Nadeo Importer'
    bl_options = {'REGISTER'}
    
    scene: StringProperty(
        default=''
    )
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        item_settings = scene.trackmania_item
        nadeo_importer_exe = str(Path(get_preferences(context).install_dir, 'NadeoImporter.exe'))
        work_dir_path = get_work_dir_path(context)
        item_path = str(SCENE_OT_TrackmaniaExportItem.get_export_path(context, scene))
        relative_item_path = os.path.relpath(item_path, work_dir_path)
        result = None
        result_type = 'INFO'
        try:
            result = subprocess.check_output([nadeo_importer_exe, 'Item', relative_item_path])
        except Exception as e:
            result = e.output
            result_type = 'ERROR_INVALID_CONTEXT'
        result = result.decode('utf-8').split('\r\n', 1)[1].replace('\r', '')[:-1]
        self.report({result_type}, result)
        return {'FINISHED'}

def parse_operator_exception(exception):
    subs0 = [('ERROR_INVALID_CONTEXT', part) for part in str(exception).split('Invalid Context Error: ')[1:]]
    subs1 = []
    for sub in subs0:
        subs = sub[1].split('Invalid Input Error: ')
        subs1.append((sub[0], subs[0]))
        subs1.extend([('ERROR_INVALID_INPUT', part) for part in subs[1:]])
    subs2 = []
    for sub in subs1:
        subs = sub[1].split('Error: ')
        subs2.append((sub[0], subs[0]))
        subs2.extend([('ERROR', part) for part in subs[1:]])
    subs3 = []
    for sub in subs2:
        subs = sub[1].split('Undefined Type: ')
        subs3.append((sub[0], subs[0]))
        subs3.extend([('ERROR', part) for part in subs[1:]])
    return [(type, msg[:-1]) for type, msg in subs3]

class SCENE_OT_TrackmaniaExport(Operator):
    bl_idname = 'trackmania.export'
    bl_label = 'All'
    bl_options = {'REGISTER'}
    
    scene: StringProperty(
        default=''
    )
    
    def call_export(self, export_op, item_settings, **kwargs):
        try:
            export_op(**kwargs)
            return 0
        except Exception as e:
            errors = parse_operator_exception(e)
            for error in errors:
                self.report({error[0]}, error[1])
            return len(errors)
    
    def execute(self, context):
        scene = context.scene if self.scene == '' else context.blend_data.scenes[self.scene]
        item_settings = scene.trackmania_item
        
        errors = 0
        
        if item_settings.export_mesh:
            errors += self.call_export(bpy.ops.trackmania.export_mesh, item_settings, scene=scene.name)
            
        if item_settings.export_mesh_params:
            errors += self.call_export(bpy.ops.trackmania.export_mesh_params, item_settings, scene=scene.name)
        if item_settings.export_icon:
            errors += self.call_export(bpy.ops.trackmania.render_icon, item_settings, scene=scene.name, save=True)
        if item_settings.export_item:
            errors += self.call_export(bpy.ops.trackmania.export_item, item_settings, scene=scene.name)
        if item_settings.export_nadeo:
            errors += self.call_export(bpy.ops.trackmania.nadeo_importer, item_settings, scene=scene.name)
        
        if errors == 0:
            self.report({'INFO'}, 'Export completed successfully')
        else:
            self.report({'WARNING'}, '{} errors encountered while completing export process.'.format(errors))
            
        return {'FINISHED'}

class SCENE_OT_TrackmaniaExportAll(Operator):
    bl_idname = 'trackmania.export_all'
    bl_label = 'All'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        for scene in context.blend_data.scenes:
            print('exporting {}'.format(scene.name))
            bpy.ops.trackmania.export(scene=scene.name)
        return {'FINISHED'}

class VIEW3D_PT_TrackmaniaItemSettings(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemSettings'
    bl_label = 'Item Settings'
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
        category.prop(item_settings, 'icon_enable_sun')
        if item_settings.icon_enable_sun:
            category.prop(item_settings, 'icon_sun_color')
            category.prop(item_settings, 'icon_sun_offset_pitch')
            category.prop(item_settings, 'icon_sun_offset_yaw')

class VIEW3D_PT_TrackmaniaItemExport(Panel):
    bl_idname = 'VIEW3D_PT_TrackmaniaItemExport'
    bl_label = 'Item Export'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trackmania'
    
    def draw(self, context):
        layout = self.layout
        item_settings = context.scene.trackmania_item
    
        layout.prop(item_settings, 'export_path')
        row = layout.row()
        row.prop(item_settings, 'export_mesh')
        row.prop(item_settings, 'export_mesh_params')
        row = layout.row()
        row.prop(item_settings, 'export_icon')
        row.prop(item_settings, 'export_item')
        row = layout.row()
        row.prop(item_settings, 'export_nadeo')
        
        row = layout.row()
        row.operator(SCENE_OT_TrackmaniaExport.bl_idname, text='Export Current Item')
        row = layout.row()
        row.operator(SCENE_OT_TrackmaniaExportAll.bl_idname, text='Export All Items')
    



classes = (
    SCENE_PG_TrackmaniaItem,
    SCENE_OT_TrackmaniaExportMesh,
    SCENE_OT_TrackmaniaExportMeshParams,
    SCENE_OT_TrackmaniaRenderIcon,
    SCENE_OT_TrackmaniaExportItem,
    SCENE_OT_TrackmaniaNadeoImporter,
    SCENE_OT_TrackmaniaExport,
    SCENE_OT_TrackmaniaExportAll,
    VIEW3D_PT_TrackmaniaItemSettings,
    VIEW3D_PT_TrackmaniaItemExport,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.trackmania_item = PointerProperty(type=SCENE_PG_TrackmaniaItem)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.trackmania_item



