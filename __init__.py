import bpy
bl_info = {
    'name': 'Trackmania 2020',
    'author': 'voblivion',
    'version': (2, 0, 1),
    'blender': (3, 5, 0),
    'location': 'View3D > Sidebar > Trackmania ; Material > Trackmania ; ...',
    'description': 'Export items to Trackmania 2020',
    'doc_url': '',
    'category': 'Import-Export'
}

from . import (operators, preferences, properties, panels)

# HACK reload
import importlib
operators = importlib.reload(operators)
preferences = importlib.reload(preferences)
properties = importlib.reload(properties)
panels = importlib.reload(panels)

modules = [operators, preferences, properties, panels]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()

if __name__ == '__main__':
    register()
