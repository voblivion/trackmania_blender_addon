bl_info = {
    'name': 'Trackmania 2020 Exporter',
    'author': 'voblivion',
    'version': (2, 0),
    'blender': (3, 5, 0),
    'location': 'View3D > Sidebar > Trackmania',
    'description': 'Tools to generate blocs b',
    'warning': 'WIP',
    'doc_url': '',
    'category': 'Game'
}

from . import (preferences, properties, panels, operators)

# HACK reload
import importlib
preferences = importlib.reload(preferences)
properties = importlib.reload(properties)
panels = importlib.reload(panels)
operators = importlib.reload(operators)

modules = [preferences, properties, panels, operators]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()

if __name__ == '__main__':
    register()
