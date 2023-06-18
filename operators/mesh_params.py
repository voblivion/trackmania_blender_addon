import os
import math
from xml.etree import ElementTree as xml
from xml.dom import minidom
from . import base

# HACK reload
import importlib
base = importlib.reload(base)


def _gamma_correct(channel):
    srgb = channel * 12.92 if channel < 0.0031308 else 1.055 * pow(channel, 1.0 / 2.4) - 0.055
    return max(min(int(srgb * 255 + 0.5), 255), 0)

def _color_to_hex(color):
    rgb = [color.r, color.g, color.b]
    result = ''
    return '{:02X}{:02X}{:02X}'.format(_gamma_correct(color.r), _gamma_correct(color.g), _gamma_correct(color.b))


class SCENE_OT_TrackmaniaExportMeshParams(base.SCENE_OT_TrackmaniaExportBase):
    bl_idname = 'trackmania.export_mesh_params'
    bl_label = 'Trackmania Export Mesh Params'
    bl_description = 'Exports .MeshParams.xml of selected items.'
    
    def export(self, context):
        objects = context.selected_objects
        item_settings = context.collection.trackmania_item
        item_path = base.SCENE_OT_TrackmaniaExportBase.get_item_path(context)
        base_path = item_path.parents[0] / 'Mesh' / item_path.name
        mesh_path = base_path.with_suffix('.fbx')
        path = base_path.with_suffix('.MeshParams.xml')
        
        # Generate XML
        xml_mesh_params = xml.Element('MeshParams')
        xml_mesh_params.set('MeshType', 'Static')
        xml_mesh_params.set('Collection', 'Stadium')
        xml_mesh_params.set('Scale', str(item_settings.scale))
        xml_mesh_params.set('FbxFile', os.path.relpath(str(mesh_path), path.parents[0]))
        
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
            xml_material.set('Link', material.trackmania_material.identifier)
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
        success = False
        try:
            path.parents[0].mkdir(parents=True, exist_ok=True)
            file = open(str(path), 'w')
            file.write(minidom.parseString(xml.tostring(xml_mesh_params)).toprettyxml())
            self.report({'INFO'}, 'Mesh params {} exported to {}.'.format(path.name, path.parents[0]))
            success = True
        except Exception as e:
            self.report({'ERROR'}, 'Failed to export mesh params {} to {}: {}'.format(path.name, path.parents[0], e))
        
        return success
