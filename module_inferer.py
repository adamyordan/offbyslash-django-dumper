import re
import imp


def find_modules_in_script(code, curr_dir=None):
    while '..' in curr_dir:
        curr_dir = curr_dir.replace('..', '.')

    potential_modules = set()

    r = r'from\s*(.*)\s*import\s*(.*)'
    matches = re.findall(r, code)
    for match in matches:
        righties = [x.strip() for x in match[1].split(',')]
        lefty = match[0].strip()

        if lefty == '':
            for righty in righties:
                potential_modules.add(righty)

        else:
            if lefty == '.' and curr_dir:
                for righty in righties:
                    potential_modules.add(curr_dir + '.' + righty)
            else:
                for righty in righties:
                    potential_modules.add(lefty.strip() + '.' + righty)

    r = r'\s*import\s*(.*)'
    matches = re.findall(r, code)
    for match in matches:
        righties = [x.strip() for x in match.split(',')]

        for righty in righties:
            potential_modules.add(righty)

    r = r'include\(\s*[\'\"]([^\s]*)[\'\"].*'
    matches = re.findall(r, code)
    for match in matches:
        potential_modules.add(match.strip())

    r = r'url\(.*[\'\"]\s*,\s*[\'\"]([^\'\"]*)[\'\"]'
    matches = re.findall(r, code)
    for match in matches:
        potential_modules.add(match)

    r = r'url\(.*[\'\"]\s*,\s*([^\'\"\s\(\)]*),+'
    matches = re.findall(r, code)
    for match in matches:
        potential_modules.add(match)

    new_potential_modules = set()
    for module in potential_modules:
        if module == '': continue
        if 'django' in module: continue
        if ' ' in module: continue
        if ')' in module: continue
        if '(' in module: continue
        module_segment = module.split('.')

        try:
            imp.find_module(module_segment[0])
            continue
        except:
            pass

        if module_segment[0] == '':
            module_segment[0] = curr_dir

        for i in range(len(module_segment)):
            new_potential_modules.add('.'.join(module_segment[:i + 1]))

    return sorted(list(new_potential_modules))
