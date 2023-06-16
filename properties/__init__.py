from . import (export, item, material, mesh)

# HACK reload
import importlib
export = importlib.reload(export)
item = importlib.reload(item)
material = importlib.reload(material)
mesh = importlib.reload(mesh)

modules = [export, item, material, mesh]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()
