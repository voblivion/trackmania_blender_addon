import functools
import pathlib
import re


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
    
    def __repr__(self):
        options = []
        if self.can_customize_color:
            options.append('Color')
        if self.can_customize_gameplay:
            options.append('Gameplay')
        if self.needs_base_material_uv:
            options.append('BaseMaterial')
        if self.needs_lightmap_uv:
            options.append('Lightmap')
        if not options:
            return '(' + self.identifier + ')'
        return '(' + self.identifier + ': ' + ' | '.join(options) + ')'

@functools.lru_cache(maxsize=1)
def get_trackmania_materials(filepath):
    file = open(filepath)

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
def get_physics_ids():
    return _get_values('physics_ids.txt')

@functools.lru_cache(maxsize=1)
def get_gameplay_ids():
    return _get_values('gameplay_ids.txt')
