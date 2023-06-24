import bpy
from . import base

# HACK reload
import importlib
base = importlib.reload(base)


class SCENE_OT_TrackmaniaExportMesh(base.SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_mesh'
    bl_label = 'Trackmania Export Mesh'
    bl_description = 'Exports .fbx mesh of selected items.'
    
    def export(self, context):
        objects = context.selected_objects
        item_settings = self.get_item_settings(context)
        item_path = base.SCENE_OT_TrackmaniaExportBase.get_item_path(context)
        path = (item_path.parents[0] / 'Mesh' / item_path.name).with_suffix('.fbx')
        
        # Ensure objects have enough UV layers
        has_material_errors = False
        for object in objects:
            if object.type != 'MESH' or not object.data.trackmania_mesh.is_visible:
                continue
            
            materials = [material for material in object.data.materials if material is not None]
            if not materials:
                self.report({'ERROR'}, 'Mesh {} is visible but has no materials.'.format(object.name))
                has_material_errors = True
                continue
            
            needs_base_material_uv = False
            needs_lightmap_uv = False
            for material in materials:
                needs_base_material_uv = needs_base_material_uv or material.trackmania_material.needs_base_material_uv
                needs_lightmap_uv = needs_lightmap_uv or material.trackmania_material.needs_lightmap_uv
            
            if needs_base_material_uv and 'BaseMaterial' not in object.data.uv_layers:
                self.report({'ERROR'}, 'Mesh {} is missing a BaseMaterial UV layer.'.format(object.name))
                has_material_errors = True
            if needs_lightmap_uv and 'Lightmap' not in object.data.uv_layers:
                self.report({'ERROR'}, 'Mesh {} is missing a Lightmap UV layer.'.format(object.name))
                has_material_errors = True
        if has_material_errors:
            return False
        
        # 1> Save/Update special objects names
        old_object_names = []
        old_socket_start = context.blend_data.objects.get('_socket_start')
        if old_socket_start is not None:
            old_socket_start.name = 'old_socket_start'
            old_object_names.append((old_socket_start, '_socket_start'))
        for object in objects:
            if object.type == 'MESH':
                old_object_names.append((object, object.name))
                object.name = object.data.trackmania_mesh.get_export_name(object.name)
        
        # Export
        success = False
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            bpy.ops.export_scene.fbx(filepath=str(path), object_types={'MESH', 'LIGHT'}, axis_up='Y', use_selection=True)
            self.report({'INFO'}, 'Mesh {} exported to {}.'.format(path.name, path.parents[0]))
            success = True
        except Exception as e:
            self.report({'ERROR'}, 'Failed to export mesh {} to {}: {}'.format(path.name, path.parents[0], e))
        
        # 1< Restore special objects names
        for object_name in old_object_names:
            object_name[0].name = object_name[1]
        
        return success
