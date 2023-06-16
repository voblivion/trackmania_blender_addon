import bpy
from . import export_operator_base
from ..utils import export
from ..utils import tm
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


class SCENE_OT_TrackmaniaExportMeshParams(export_operator_base._SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_mesh_params'
    bl_label = 'Export Mesh Params'
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
        path = base_path / sub_path.parents[0] / 'Mesh' / sub_path.name
        
        mesh_path_name = str(base_path / sub_path.parents[0] / 'Mesh' / sub_path.name) + '.fbx'
        
        # Generate XML
        xml_mesh_params = xml.Element('MeshParams')
        xml_mesh_params.set('MeshType', 'Static')
        xml_mesh_params.set('Collection', 'Stadium')
        xml_mesh_params.set('Scale', str(item_settings.scale))
        xml_mesh_params.set('FbxFile', os.path.relpath(mesh_path_name, path.parents[0]))
        
        # .1 Generate Materials section
        xml_materials = xml.SubElement(xml_mesh_params, 'Materials')
        materials = set()
        for object in objects:
            for material_slot in object.material_slots:
                material = material_slot.material
                if materials is not None:
                    materials.add(material)
        
        for material in materials:
            xml_material = xml.SubElement(xml_materials, 'Material')
            xml_material.set('Name', material.name)
            xml_material.set('Link', material.trackmania_material.material)
            xml_material.set('Color', _color_to_hex(material.trackmania_material.color))
            if material.trackmania_material.gameplay != 'None':
                xml_material.set('GameplayId', str(material.trackmania_material.gameplay))
            if material.trackmania_material.physics != 'Default':
                xml_material.set('PhysicsId', str(material.trackmania_material.physics))
            
        # .2 Generate Lights section
        xml_lights = xml.SubElement(xml_mesh_params, 'Lights')
        for object in objects:
            if object.type != 'LIGHT' or object.data.type not in ['POINT', 'SPOT']:
                continue
            
            light = object.data
            
            xml_light = xml.SubElement(xml_lights, 'Light')
            xml_light.set('sRGB', _color_to_hex(light.color))
            xml_light.set('Name', object.name)
            xml_light.set('Intensity', str(light.energy))
            xml_light.set('Distance', str(light.distance))
            if light.type == 'POINT':
                xml_light.set('Type', 'Point')
            else:
                xml_light.set('Type', 'Spot')
                xml_light.set('SpotOuterAngle', str(math.degrees(light.spot_size)))
                xml_light.set('SpotInnerAngle', str(sqrt(1-light.spot_blend) * math.degrees(light.spot_size)))
        
        # Export
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            file = open(str(path) + '.MeshParams.xml', 'w')
            file.write(minidom.parseString(xml.tostring(xml_mesh_params)).toprettyxml())
            self.report({'INFO'}, 'Mesh params exported successfully: ' + str(path) + '.MeshParams.xml.')
        except Exception as e:
            self.report({'ERROR'}, 'Error occured while exporting mesh params: ' + str(e))
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCENE_OT_TrackmaniaExportMeshParams)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_TrackmaniaExportMeshParams)
