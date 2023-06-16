from . import (export, item, light, material, mesh, operations)

# HACK reload
import importlib
export = importlib.reload(export)
item = importlib.reload(item)
light = importlib.reload(light)
material = importlib.reload(material)
mesh = importlib.reload(mesh)
operations = importlib.reload(operations)

modules = [export, item, light, material, mesh, operations]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()
