import bpy
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty, EnumProperty, FloatVectorProperty, PointerProperty)

import functools
import pathlib
import re

from ..utils import preferences

# HACK
from importlib import reload
preferences = reload(preferences)


@functools.lru_cache(maxsize=1)
def _get_gameplay_compatible_materials():
    path = pathlib.Path(__file__).parent / 'gameplay_compatible_materials.txt'
    file = open(path)
    lines = file.readlines()
    return [line.split('\n')[0] for line in lines]

class TrackmaniaMaterial():
    def __init__(self, identifier):
        self.identifier = identifier
        self.can_customize_color = 'Custom' in identifier
        self.can_customize_gameplay = identifier in _get_gameplay_compatible_materials()
        self.needs_base_material_uv = False
        self.needs_lightmap_uv = False

@functools.lru_cache(maxsize=1)
def _get_trackmania_materials(context):
    install_dir = preferences.get(context).install_dir
    path = pathlib.Path(install_dir) / 'NadeoImporterMaterialLib.txt'
    file = open(path)
    
    materials = {}
    material = None
    lines = file.readlines()
    for line in lines:
        tokens = [token.strip() for token in re.split('\(|\)|,', line)]
        if len(tokens) < 2:
            continue
        if tokens[0] == 'DMaterial':
            materials[tokens[1]] = TrackmaniaMaterial(tokens[1])
            material = materials[tokens[1]]
        elif tokens[0] == 'DUvLayer':
            if tokens[1] == 'BaseMaterial':
                material.needs_base_material_uv = True
            elif tokens[1] == 'Lightmap':
                material.needs_lightmap_uv = True
    return materials

def _get_values(filename):
    path = pathlib.Path(__file__).parent / filename
    file = open(path)
    lines = file.readlines()
    return [line.split('\n')[0].split(': ') for line in lines]

@functools.lru_cache(maxsize=1)
def _get_physics_ids():
    return _get_values('physics_ids.txt')

@functools.lru_cache(maxsize=1)
def _get_gameplay_ids():
    return _get_values('gameplay_ids.txt')

class MATERIAL_PG_TrackmaniaMaterial(PropertyGroup):
    bl_idname = 'MATERIAL_PG_TrackmaniaMaterial'
    
    def _get_identifiers(self, context):
        return [(identifier, identifier, '') for identifier in _get_trackmania_materials(context)]
    
    @property
    def needs_base_material_uv(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].needs_base_material_uv
    
    @property
    def needs_lightmap_uv(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].needs_lightmap_uv
    
    identifier: EnumProperty(
        items=_get_identifiers,
        name='Identifier',
        description='A Trackmania material supported by NadeoImporter.',
        default=0,
    )
    
    physics: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in _get_physics_ids()],
        name='Physics',
        description='Overrides the way the cars will interact physically with the surface. You should not overuse this feature because it is usually a bad idea (for gameplay and fun) to have a surface looking like grass but behaving like dirt.',
        default='Default'
    )
    
    @property
    def can_customize_gameplay(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].can_customize_gameplay
    
    gameplay: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in _get_gameplay_ids()],
        name='Gameplay',
        description='Setting a value different than None will add a special gameplay effect to the surface, like activating free wheeling or slow motion modes. Some of those gameplay effects such as Turbo or ReactorBoost are "oriented": the direction of this effect is automatically the local z-axis of the item.',
        default='None'
    )
    
    @property
    def can_customize_color(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].can_customize_color
    
    color: FloatVectorProperty(
        name='Color',
        description='Color for Custom materials',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        default=(1, 1, 1)
    )
