import os
import re
import difflib
import shutil

def _similarity(lhs, rhs):
    return difflib.SequenceMatcher(None, lhs, rhs).ratio()

suffixes = ['_D', '_I', '_T', '']
forbidden_suffixes = ['_G', '_H', '_R', '_N', '_HueMask', '_X2']

class Keyword:
    def __init__(self, material, bonus, texture=None, malus=None):
        self.material = material
        self.bonus = bonus
        self.texture = texture if texture is not None else material
        self.malus = malus if malus is not None else -bonus
    
    def match(self, material, texture, debug=False):
        m = re.search(self.material, material) is not None
        t = re.search(self.texture, texture) is not None
        if t and m:
            return self.bonus
        elif t != m:
            return self.malus
        else:
            return 0.0

keywords = [
    # Sizes
    Keyword('8x1', 2),
    Keyword('4x1', 2),
    Keyword('2x1', 2),
    Keyword('1x1', 2, '1x1', 0),
    
    # Type
    Keyword('Decal', 1.5),
    Keyword('Trigger', 1),
    Keyword('Special', 1),
    Keyword('FX', 1),
    Keyword('Platform', 1),
    Keyword('Border', 1.5),
    Keyword('Track', 1),
    Keyword('Item', 0.5),
    Keyword('LampLight', 1, 'Lamp'),
    #Keyword('(((?!Lamp).){4}Light|^.{0,3}Light)', 1, 'Light'),
    Keyword('Sign', 1),
    Keyword('Ad', 1.0),
    Keyword('DecoHill', 2.0),
    Keyword('Curve', 2),

    
    # Effects
    Keyword('Cruise', 2),
    Keyword('Turbo', 2),
    Keyword('Boost', 2),
    Keyword('Reset', 2),
    Keyword('Fragile', 2),
    Keyword('NoBrake', 2),
    Keyword('NoEngine', 2),
    Keyword('NoSteering', 2),
    Keyword('SlowMotion', 2),
    Keyword('Roulette', 2),
    
    # Versions
    Keyword('A$', 1, 'A_[A-Z].dds$'),
    Keyword('B$', 1, 'B_[A-Z].dds$'),
    Keyword('C$', 1, 'C_[A-Z].dds$'),
    Keyword('D$', 1, 'D_[A-Z].dds$'),
    Keyword('([^xX])2([^x]|$)', 1),
    
    # Surface
    Keyword('Chrono', 2),
    Keyword('Checkpoint', 2),
    Keyword('Finish', 2),
    Keyword('Start', 2),
    Keyword('Tech', 2, 'Tech', -1),
    Keyword('Dirt', 2),
    Keyword('Ice', 2),
    Keyword('Grass', 2),
    Keyword('Screen', 2),
    Keyword('Plastic', 3),
    Keyword('Glass', 2),
    Keyword('Concrete', 2),
    Keyword('Bricks', 2),
    Keyword('Metal', 2),
    Keyword('Rock', 2),
    Keyword('Sand', 2),
    Keyword('Snow', 2),
    Keyword('RoughWood', 2),
    Keyword('Pool', 2, '(Water|Pool)'),
    Keyword('SelfIllum', 2),
    
    # Other
    Keyword('Off', 1.0),
    Keyword('Down', 1.0),
    Keyword('Small', 1),
    Keyword('Simple', 1),
    Keyword('Custom', 0.5),
    Keyword('Py', 1),
    Keyword('PlatformDirt_Platform', 2, 'DirtPy'),
]

good_enough = [
    '16x9ScreenOff',
]

def _get_trackmania_materials():
    path = './NadeoImporterMaterialLib.txt'
    file = open(path)

    materials = set()
    lines = file.readlines()
    for line in lines:
        tokens = [token.strip() for token in re.split('\(|\)|,', line)]
        if len(tokens) < 2:
            continue
        if tokens[0] == 'DMaterial':
            materials.add(tokens[1])
    return materials

def first(e):
    return e[0]

def second(e):
    return -e[1]

def main():
    all_materials = _get_trackmania_materials()
    all_textures = os.listdir('Image')
    
    perfect_materials = []
    partial_materials = []
    
    for material in all_materials:
        texture = None
        for suffix in suffixes:
            if material + suffix + '.dds' in all_textures:
                texture = material + suffix + '.dds'
                break
        
        if texture:
            perfect_materials.append((material, texture))
            continue
        
        textures = []
        for texture in all_textures:
            s = 0
            found_keywords = []
            extra_keywords = []
            for keyword in keywords:
                d = keyword.match(material, texture)
                s = s + d
                if d > 0.0:
                    found_keywords.append(keyword.material)
                elif d < 0.0:
                    extra_keywords.append(keyword.material)
            found_suffix = False
            for i in range(0, len(suffixes)):
                if suffixes[i] + '.dds' in texture:
                    s = s - i * 1.0 / len(suffixes) * 0.5
                    found_suffix = True
                    break
            if not found_suffix:
                s = s - 0.5
            textures.append((texture, s, found_keywords, extra_keywords))
        textures = sorted(textures, key=second)
        
        # filter within 50% of best score
        textures = [texture for texture in textures if texture[1] > textures[0][1] - 1]
        
        # filter texture types
        for suffix in suffixes:
            s = suffix + '.dds'
            to_remove = []
            for texture in textures:
                if texture[0][-len(s):] == s:
                    for other in textures:
                        if other[0][:-len(s)] == texture[0][:-len(s)] and other[0] != texture[0]:
                            to_remove.append(other[0])
            textures = [texture for texture in textures if texture[0] not in to_remove]
        for forbidden_suffix in forbidden_suffixes:
            s = forbidden_suffix + '.dds'
            textures = [texture for texture in textures if s not in texture[0]]
        
        textures = [textures[0]] if material in good_enough else textures
        textures = [texture for texture in textures if texture[2]]
        partial_materials.append((material, textures))
    
    total = 0
    partial_materials = sorted(partial_materials, key=first)
    
    final_materials = perfect_materials
    for m in partial_materials:
        if len(m[1]) == 1:
            final_materials.append((m[0], m[1][0][0]))
    
    final_materials = sorted(final_materials, key=first)
    
    file = open('default_material_textures.txt', 'w')
    for m in final_materials:
        file.write(m[0] + ',' + m[1] + '\n')
        shutil.copy('Image/' + m[1], 'Processed/' + m[1])
    
if __name__ == '__main__':
    main()