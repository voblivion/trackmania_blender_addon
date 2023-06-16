import bpy
from bpy.props import (BoolProperty, PointerProperty, StringProperty)
import itertools
import math
import mathutils
from . import export_operator_base
from ..utils import export
from ..utils.math import (get_vectors_center, get_objects_bounds, inverse_matrix)

# HACK reload
import importlib
export = importlib.reload(export)
export_operator_base = importlib.reload(export_operator_base)

def _offset_look_at(object, bounds_w, pitch, yaw):
    center_position_w = get_vectors_center(bounds_w)
    center_matrix_w = mathutils.Matrix.Translation(center_position_w)
    radius = max([bound.length for bound in bounds_w])
    object_position_c = mathutils.Matrix.Rotation(math.radians(yaw), 4, 'Z') \
        @ mathutils.Matrix.Rotation(math.radians(pitch), 4, 'Y') \
        @ mathutils.Vector((-1 - 2 * radius, 0, 0))
    object_position_matrix_c = mathutils.Matrix.Translation(object_position_c)
    object_look_at_matrix = (-object_position_c).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
    object_matrix_w = center_matrix_w @ object_position_matrix_c @ object_look_at_matrix
    object.matrix_world = object_matrix_w

def _is_main_object(object):
    return object.trackmania_export.export_type in ['SEPARATE', 'UNIQUE']

class SCENE_OT_TrackmaniaExportIcon(export_operator_base._SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_icon'
    bl_label = 'Export Icon'
    bl_options = {'REGISTER'}
    
    save: BoolProperty(name='Save', default=True)
    
    def execute(self, context):
        scene = context.scene
        objects = context.view_layer.objects.selected
        collection = context.collection
        item_settings = collection.trackmania_item
        
        # Generate Path
        base_path = export.get_base_export_path(context)
        sub_path = self.get_sub_path(context)
        if sub_path is None:
            return {'CANCELLED'}
        path = base_path / sub_path.parents[0] / 'Icon' / sub_path.name
        
        # Calculate visible bounds
        visible_objects = []
        for object in objects:
            if not object.hide_render and object.type == 'MESH':
                visible_objects.append(object)
        bounds_w = get_objects_bounds(visible_objects)
        if not bounds_w:
            self.report({'ERROR'}, 'No visible objects to render.')
            return {'CANCELLED'}
        
        # Ensure we can have a camera
        user_camera = next((object for object in objects if object.type == 'CAMERA'), None)
        if not item_settings.icon_enable_camera and not custom_camera:
            self.report({'ERROR'}, 'No camera to render icon and generated camera is not enabled.')
            return {'CANCELLED'}
        
        # 1> Save/Update current render settings
        old_scene_render_resolution_x = scene.render.resolution_x
        old_scene_render_resolution_y = scene.render.resolution_y
        old_scene_render_film_transparent = scene.render.film_transparent
        old_scene_render_image_settings_file_format = scene.render.image_settings.file_format
        
        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = 'TARGA'
        
        # 2> Create custom camera
        custom_camera_object = None
        if item_settings.icon_enable_camera:
            custom_camera = bpy.data.cameras.new('Camera')
            custom_camera.type = 'ORTHO'
            camera_object = bpy.data.objects.new('Camera', custom_camera)
            collection.objects.link(camera_object)
            _offset_look_at(camera_object, bounds_w, item_settings.icon_camera_pitch, item_settings.icon_camera_yaw)
            item_matrix_v = inverse_matrix(camera_object.matrix_world)
            bounds_v = [item_matrix_v @ vector for vector in bounds_w]
            custom_camera.ortho_scale = 2 * max(itertools.chain((abs(pos.x) for pos in bounds_v), (abs(pos.y) for pos in bounds_v)))
            custom_camera_object = camera_object
            
        # 3> Save/Update camera
        old_scene_camera = scene.camera
        
        scene.camera = custom_camera_object if custom_camera_object else user_camera
        
        # 4> Save/Update objects visibility
        old_object_visibility = []
        for object in objects:
            if object.type == 'MESH' and not object.hide_render and not object.data.trackmania_mesh.render_on_icon:
                old_visible_invisible_objects.append(object)
                object.hide_render = True
            if object.type == 'MESH' and object.hide_render and object.data.trackmania_mesh.render_on_icon:
                old_visible_invisible_objects.append(object)
                object.hide_render = False
        
        # 5> Create custom sun
        custom_sun_object = None
        if item_settings.icon_enable_sun:
            sun_light = bpy.data.lights.new('Sun', type='SUN')
            sun_light.energy = 3
            sun_light.color = item_settings.icon_sun_color
            custom_sun_object = bpy.data.objects.new('Sun', sun_light)
            collection.objects.link(custom_sun_object)
            _offset_look_at(
                custom_sun_object,
                bounds_w,
                item_settings.icon_camera_pitch + item_settings.icon_sun_offset_pitch,
                item_settings.icon_camera_yaw + item_settings.icon_sun_offset_yaw)
        
        # 6> Save/Update render path
        old_scene_render_filepath = scene.render.filepath
        scene.render.filepath = str(path)
        
        # Export
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            bpy.ops.render.render(scene=scene.name, write_still=self.save)
            self.report({'INFO'}, 'Icon exported successfully: ' + str(path) + '.tga.')
        except Exception as e:
            self.report({'ERROR'}, 'Error occured while exporting icon: ' + str(e))
        
        # 6< Restore render path
        scene.render.filepath = old_scene_render_filepath
        
        # 5< Destroy custom sun
        if item_settings.icon_enable_sun:
            bpy.data.objects.remove(custom_sun_object)
        
        # 4< Restore objects visibility
        for object in old_object_visibility:
            object.hide_render = not object.hide_render
        
        # 3< Restore previous camera
        scene.camera = old_scene_camera
        
        # 2< Destroy custom camera
        if item_settings.icon_enable_camera:
            bpy.data.objects.remove(custom_camera_object)
        
        # 1< Restore previous render settings
        scene.render.resolution_x = old_scene_render_resolution_x
        scene.render.resolution_y = old_scene_render_resolution_y
        scene.render.film_transparent = old_scene_render_film_transparent
        scene.render.image_settings.file_format = old_scene_render_image_settings_file_format
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaExportIcon)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaExportIcon)
