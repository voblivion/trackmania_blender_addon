import functools
import pathlib
import re

class TmMaterial():
    def __init__(self, name):
        self.name = name
        self.allows_color = name[:6] == 'Custom'
        self.needs_base_material_uv = False
        self.needs_lightmap_uv = False

@functools.lru_cache(maxsize=1)
def get_tm_materials(context):
    path = pathlib.Path(context.preferences.addons['Trackmania'].preferences.install_dir, 'NadeoImporterMaterialLib.txt')
    file = open(path)
    
    tm_materials = {}
    tm_material = None
    lines = file.readlines()
    for line in lines:
        tokens = [token.strip() for token in re.split('\(|\)|,', line)]
        if len(tokens) < 2:
            continue
        if tokens[0] == 'DMaterial':
            tm_materials[tokens[1]] = TmMaterial(tokens[1])
            tm_material = tm_materials[tokens[1]]
        elif tokens[0] == 'DUvLayer':
            if tokens[1] == 'BaseMaterial':
                tm_material.needs_base_material_uv = True
            elif tokens[1] == 'Lightmap':
                tm_material.needs_lightmap_uv = True
    return tm_materials

physics_ids = [
    ('Default', 'no override, default physics of material'),
    ('Asphalt', 'the actual base material of TrackMania, used on every normal road and platforms'),
    ('Concrete', '"base" material, but not used for base roads in TM !'),
    ('Dirt', 'used in dirt blocks'),
    ('Grass', 'used in the default grass of the stadium (not to be mistaken with Green surfaces) and as a speed penalty surface'),
    ('Green', 'used in synthetic grass platforms (not to be mistaken with Grass surfaces)'),
    ('Ice', 'used in the colorable CustomIce material'),
    ('Metal', 'used in black platform blocks'),
    ('MetalTrans', 'mostly used on screens'),
    ('NotCollidable', 'used for decals, to... not be collidable. But instead of using this PhysicsId, you should rather use the _notcollidable_ prefix in your fbx objects, as described in section How to create the fbx file.'),
    ('Pavement', 'used in the colorable CustomBricks material'),
    ('Plastic', 'used in inflatable items introduced in June 2021 update'),
    ('ResonantMetal', 'also used in black platform blocks, usually makes a noise on collision'),
    ('RoadIce', 'used in "bobsleigh" ice blocks'),
    ('RoadSynthetic', 'used in bump roads'),
    ('Rock', 'used in colorable CustomRock material'),
    ('Rubber', 'used on the sides of the roads, gives speed penalty when hit'),
    ('Sand', 'used as a speed penalty surface in dirt platform blocks'),
    ('Snow', 'used in colorable CustomSnow material and as a speed penalty surface'),
    ('TechMagnetic', 'not used in any game material, makes the car attracted to that surface'),
    ('TechMagneticAccel', 'not used in any game material, makes the car attracted to that surface and gives it a better acceleration while on it'),
    ('TechSuperMagnetic', 'not used in any game material, makes the car attracted strongly to that surface'),
    ('Wood', 'used in colorable CustomRoughWood material')
]

gameplay_override_compatible_materials = (
    'PlatformDirt_PlatformTech',
    'PlatformGrass_PlatformTech',
    'PlatformIce_PlatformTech',
    'PlatformTech',
    'RoadBump',
    'RoadDirt',
    'RoadIce',
    'RoadTech'
)

gameplay_ids = [
    ('None', 'no gameplay effect (this is the default value for all game materials)'),
    ('Bumper', 'makes the car bump a bit'),
    ('Bumper2', 'makes the car bump a lot'),
    ('Cruise', 'makes the car maintain its speed'),
    ('ForceAcceleration', 'disables breaking until next Reset block or next checkpoint'),
    ('Fragile', 'makes the car sensitive to hard bumps and crashes, making it harder to handle and accelerate the more damages it takes. Only gets back to normal with a Reset Block'),
    ('FreeWheeling', 'entirely stops the engine until next Reset block or next checkpoint'),
    ('NoBrakes', 'disables the car brakes'),
    ('NoGrip', 'comparable to ice, but way less handling and no drift mechanic until next Reset block or next checkpoint'),
    ('NoSteering', 'disables steering until next Reset block or next checkpoint'),
    ('ReactorBoost', 'activates flames at the sides of the wheels that push the car upwards or downwards for some time or until next Reset block (direction of ReactorBoost is along Z-axis', 'towards positive Z is ReactorBoost Up and towards negative is ReactorBoost Down)'),
    ('ReactorBoost2', 'same effect as ReactorBoost, but stronger'),
    ('Reset', 'disables any ongoing gameplay effects'),
    ('SlowMotion', 'slows down the behaviour of the car (but not the timer) for some time or until next Reset block'),
    ('Turbo', '"yellow turbo" blocks, sudden burst of acceleration (direction of Turbo is North / along Z-axis)'),
    ('Turbo2', '"red turbo" blocks, stronger burst of acceleration (direction of Turbo2 is North / along the Z-axis)')
]
