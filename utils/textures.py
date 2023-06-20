import pathlib
import functools
import os
import pathlib
import re
from ..utils import materials as material_utils

def _read_ini(filepath):
    file = open(filepath)
    lines = file.readlines()
    
    section_name = ''
    sections = {}
    
    for line in lines:
        # Ignore newline character
        content = line[:-1] if line[-1] == '\n' else line
        
        # Ignore comments
        content = content.split('#')[0]
        
        # Ignore trailing spaces
        content = content.strip()
        
        # Ignore empty lines
        if content == '':
            continue
        
        # New Section
        section_result = re.search(r'^\[(\w+)\]$', content)
        if section_result:
            section_name = section_result.group(1)
            continue
        
        # List section
        if content[0] == '-':
            if section_name not in sections:
                sections[section_name] = []
            section = sections[section_name]
            if not isinstance(section, list):
                print('ERROR: invalid ini file, mixing list and dictionary sections.')
                continue
            section.append(content[1:].strip())
        # Dict section
        else:
            if section_name not in sections:
                sections[section_name] = {}
            section = sections[section_name]
            if not isinstance(section, dict):
                print('ERROR: invalid ini file, mixing list and dictionary sections.')
                continue
            name_value_result = re.search(r'^(\w+)(?:\:(.*))?$', content)
            if not name_value_result:
                print('ERROR: invalid init file, not a valid key.')
                continue
            name = name_value_result.group(1).strip()
            value = name_value_result.group(2)
            value = value.strip() if value is not None else None
            section[name] = value
    return sections

class Keyword:
    def __init__(self, material, bonus, texture=None, malus=None):
        self.material = material
        self.bonus = float(bonus)
        self.texture = texture if texture is not None else material
        self.malus = float(malus) if malus is not None else -self.bonus
    
    def __repr__(self):
        return '(r:' + self.material + ', ' + str(self.bonus) + ', r:' + self.texture + ', ' + str(self.malus) + ')'
    
    def match(self, material, texture, debug=False):
        m = re.search(self.material, material) is not None
        t = re.search(self.texture, texture) is not None
        if t and m:
            return self.bonus
        elif t != m:
            return self.malus
        else:
            return 0.0

def _read_default_materials_ini(filepath):
    texture_dirs = []
    preferred_suffixes = []
    forbidden_suffixes = set()
    keywords = []
    
    ini = _read_ini(filepath)
    if 'TEXTURE_DIRS' in ini:
        texture_dirs = ini['TEXTURE_DIRS']
    if 'SUFFIXES' in ini:
        suffixes = ini['SUFFIXES']
        if 'preferred' in suffixes:
            preferred_suffixes = [s.strip() for s in suffixes['preferred'].split(',')]
        if 'forbidden' in suffixes:
            forbidden_suffixes = set([s.strip() for s in suffixes['forbidden'].split(',')])
    if 'KEYWORDS' in ini and isinstance(ini['KEYWORDS'], list):
        keywords = [Keyword(*entry.split(',')) for entry in ini['KEYWORDS']]
    
    return texture_dirs, preferred_suffixes, forbidden_suffixes, keywords

def _get_default_material_textures(materials_filepath, ini_filepath, openplanet_extract_dir):
    texture_dirs, preferred_suffixes, forbidden_suffixes, keywords = _read_default_materials_ini(ini_filepath)
    
    all_textures = []
    for texture_dir in texture_dirs:
        texture_dir = pathlib.Path(openplanet_extract_dir) / texture_dir
        texture_filenames = os.listdir(texture_dir)
        all_textures.extend([texture_dir / texture_filename for texture_filename in texture_filenames])
    
    all_materials = material_utils.get_trackmania_materials(materials_filepath)
    ext = '.dds'
    worst_suffix_malus = -0.1
    
    # 1. Ignore textures with forbidden suffixes
    allowed_textures = []
    for texture in all_textures:
        has_forbidden_suffix = False
        for fs in forbidden_suffixes:
            if texture.name[-len(fs + ext):] == fs + ext:
                has_forbidden_suffix = True
                break
        if not has_forbidden_suffix:
            allowed_textures.append(texture)
    
    # 2. Find a texture for each material
    perfect_matches = []
    all_matches = []
    for material in all_materials:
        # 2.1. Perfect matches
        texture = None
        for ps in preferred_suffixes:
            texture = next((t for t in allowed_textures if t.name == material + ps + ext), None)
            if texture:
                perfect_matches.append((material, texture))
                all_matches.append((material, texture))
                break
        if texture:
            continue
        # 2.2. Imperfect matches
        # 2.2.1 Calculate score for every textures
        best_textures = []
        for texture in allowed_textures:
            score = 0
            bonus_keywords = []
            malus_keywords = []
            # 2.2.1.1 Keyword scores
            for keyword in keywords:
                keyword_score = keyword.match(material, texture.name)
                score = score + keyword_score
                if keyword_score > 0.0:
                    bonus_keywords.append(keyword)
                elif keyword_score < 0.0:
                    malus_keywords.append(keyword)
            # 2.2.1.2 Suffix scores
            has_suffix = False
            for preferred_suffix_index in range(0, len(preferred_suffixes)):
                ps = preferred_suffixes[preferred_suffix_index]
                if texture.name[-len(ps + ext):] == ps + ext:
                    score = score + preferred_suffix_index / len(preferred_suffixes) * worst_suffix_malus
                    has_suffix = True
                    break
            if not has_suffix:
                score = score + worst_suffix_malus
            best_textures.append((texture, score, bonus_keywords, malus_keywords))
        
        # 2.2.2 Isolate best textures
        best_textures = sorted(best_textures, key=lambda best_texture: -best_texture[1])
        best_textures = [t for t in best_textures if t[1] == best_textures[0][1] and t[1] > 0.0]
        
        # 2.2.3 Got exactly one best texture
        if len(best_textures) == 1:
            all_matches.append((material, best_textures[0][0]))
        else:
            print('Cannot find a best texture for ' + material + ':')
            for best_texture in best_textures:
                print('-', best_texture[0].name, best_texture[2], best_texture[3])
    
    all_matches = sorted(all_matches, key=lambda match: match[0])
    for m in all_matches:
        print(m)
    print('valid textures:', len(allowed_textures), '/', len(all_textures))
    print('perfect matches:', len(perfect_matches) , '/', len(all_materials))
    print('all matches:', len(all_matches) , '/', len(all_materials))
    return all_matches

@functools.lru_cache(maxsize=1)
def get_default_material_textures(materials_filepath, openplanet_extract_dir):
    return _get_default_material_textures(
        materials_filepath,
        pathlib.Path(__file__).parent / 'default_textures.ini',
        openplanet_extract_dir
    )
