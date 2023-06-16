import bpy
from . import export_operator_base
from ..utils import export
from ..utils import tm
from ..utils import preferences
import os
import math
from xml.etree import ElementTree as xml
from xml.dom import minidom

# HACK reload
import importlib
export = importlib.reload(export)
export_operator_base = importlib.reload(export_operator_base)


def _gamma_correct(channel):
    srgb = channel * 12.92 if channel < 0.0031308 else 1.055 * pow(channel, 1.0 / 2.4) - 0.055
    return max(min(int(srgb * 255 + 0.5), 255), 0)

def _color_to_hex(color):
    rgb = [color.r, color.g, color.b]
    result = ''
    return '{:02X}{:02X}{:02X}'.format(_gamma_correct(color.r), _gamma_correct(color.g), _gamma_correct(color.b))


class SCENE_OT_TrackmaniaExportItem(export_operator_base._SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_item'
    bl_label = 'Export Item'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        objects = context.view_layer.objects.selected
        collection = context.collection
        item_settings = collection.trackmania_item
        
        # Generate Path
        base_path = export.get_base_export_path(context)
        sub_path = self.get_sub_path(context)
        if sub_path is None:
            return {'CANCELLED'}
        path = base_path / sub_path
        
        mesh_params_path_name = str(base_path / sub_path.parents[0] / 'Mesh' / sub_path.name) + '.MeshParams.xml'
        
        # Generate XML
        xml_item = xml.Element('Item')
        xml_item.set('Type', 'StaticObject')
        xml_item.set('Collection', 'Stadium')
        xml_item.set('AuthorName', preferences.get(context).author_name)
        
        # .1 MeshParamsLink
        xml_mesh_params_link = xml.SubElement(xml_item, 'MeshParamsLink')
        xml_mesh_params_link.set('File', os.path.relpath(mesh_params_path_name, path.parents[0]))
        
        # .2 Waypoint
        if item_settings.waypoint_type != 'NONE':
            xml_waypoint = xml.SubElement(xml_item, 'Waypoint')
            xml_waypoint.set('Type', item_settings.waypoint_type)
        
        # .3 Pivots
        xml_pivots = xml.SubElement(xml_item, 'Pivots')
        for object in objects:
            if object.type != 'EMPTY':
                continue
            
            xml_pivot = xml.SubElement(xml_pivots, 'Pivot')
            xml_pivot.set('Pos ', '{} {} {}'.format(object.location.x, object.location.z, -object.location.y))
        
        # .4 PivotSnap
        if not item_settings.pivot_automatic_snap:
            xml_pivot_snap = xml.SubElement(xml_item, 'PivotSnap')
            xml_pivot_snap.set('Distance', str(item_settings.pivot_snap_distance))
        
        # .5 GridSnap
        xml_grid_snap = xml.SubElement(xml_item, 'GridSnap')
        xml_grid_snap.set('HStep', str(item_settings.grid_horizontal_step))
        xml_grid_snap.set('HOffset', str(item_settings.grid_horizontal_offset))
        xml_grid_snap.set('VStep', str(item_settings.grid_vertical_step))
        xml_grid_snap.set('VOffset', str(item_settings.grid_vertical_offset))
        
        # .6 Levitation
        xml_levitation = xml.SubElement(xml_item, 'Levitation')
        xml_levitation.set('VStep', str(item_settings.fly_step))
        xml_levitation.set('VOffset', str(item_settings.fly_offset))
        xml_levitation.set('GhostMode', str(item_settings.ghost_mode).lower())
        
        # .7 Options
        xml_options = xml.SubElement(xml_item, 'Options')
        xml_options.set('ManualPivotSwitch', str(item_settings.pivot_manual_switch).lower())
        xml_options.set('OneAxisRotation', str(item_settings.one_axis_rotation).lower())
        xml_options.set('AutoRotation', str(item_settings.auto_rotation).lower())
        xml_options.set('NotOnItem', str(item_settings.not_on_item).lower())
        
        # Export
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            file = open(str(path) + '.Item.xml', 'w')
            file.write(minidom.parseString(xml.tostring(xml_item)).toprettyxml())
            self.report({'INFO'}, 'Item exported successfully: ' + str(path) + '.Item.xml.')
        except Exception as e:
            self.report({'ERROR'}, 'Error occured while exporting item: ' + str(e))
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaExportItem)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaExportItem)
