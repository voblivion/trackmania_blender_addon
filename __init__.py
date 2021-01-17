bl_info = {
    'name': 'Trackmania',
    'author': 'voblivion',
    'version': (1, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Sidebar > Trackmania',
    'description': 'Tools to generate blocs b',
    'warning': 'WIP',
    'doc_url': '',
    'category': 'Game'
}

from . import (
    preferences,
    part,
    material,
    item,
    menu
)

# HACK reload
import importlib
preferences = importlib.reload(preferences)
part = importlib.reload(part)
item = importlib.reload(item)
material = importlib.reload(material)
menu = importlib.reload(menu)

modules = [preferences, part, material, item, menu]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()

if __name__ == '__main__':
    register()




