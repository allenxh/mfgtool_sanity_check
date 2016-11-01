import os
import xml.etree.ElementTree as ET
import re
import pdb

list_name = "Quad Nor Flash"
createvar = globals()

def locate_keywords(line, key):
    if line.lower().find(key.lower()) >= 0:
        return 1
    else:
        return 0

def parse_list_from_vbs(fp):
        for line in iter(fp):
            if locate_keywords(line, "mfgtool2"):
                break
        vars = iter(line.split('""'))
        while True:
            if locate_keywords(vars.next(), "-l"):
                break 
        return vars.next()

def update_globals(line):
    var_name = line.split('=')[0].strip()
    var_value = line.split('=')[1].strip()
    if var_value:
        createvar[var_name] = var_value
    else:
        if var_name in globals():
            del globals()[var_name]

def parse_cfg_ini():
    with open('cfg.ini') as fp:
        for line in iter(fp):
            if locate_keywords(line, "variable"):
                break
        for line in iter(fp):
            update_globals(line)

def update_globals_from_vbs(fp):
        for line in iter(fp):
            if locate_keywords(line, "mfgtool2"):
                break
        vars = iter(line.split('""'))
        while True:
            try:
                var = vars.next()
            except StopIteration:
                break
            if locate_keywords(var, "-s"):
                update_globals(vars.next())

def locate_child_node(root, key):
    for child in root:
        if child.tag == 'LIST':
            if child.attrib['name'] == key:
                return child

def parse_files_from_list(list):
    for child in list:
        #  try: child.attrib['file']:
        try:
            file_name = child.attrib['file']

            for var in re.finditer('%.*?%', child.attrib['file']):
                try:
                    #  print((var.group(0), globals()[var.group(0).strip("%")]))
                    new_file_name = file_name.replace(var.group(0), globals()[var.group(0).strip('%')], 1)
                    file_name = new_file_name
                    #  print file_name
                except:
                    #  print ("\x1b[1;33;40mWARNNING %s\x1b[0m not defined" % var.group(0))
                    new_file_name = file_name.replace(var.group(0), '', 1)
                    file_name = new_file_name


        except:
            continue
        file_path = "Profiles/Linux/OS Firmware/" + file_name
        if not os.path.exists(file_path):
            print("%s \x1b[1;31;40m[missed]\x1b[0m" % (file_path))
            return False
    return True

def main():
    #  open the ucl2.xml
    tree = ET.parse('Profiles/Linux/OS Firmware/ucl2.xml')
    root = tree.getroot()
    #  recursively search vbs files
    for file in os.listdir("./"):
        if file.endswith(".vbs"):
            if file.find('yocto') >= 0:
                # parse the cfg ini
                parse_cfg_ini()
                #  update variables from vbs
                with open(file) as fp:
                    update_globals_from_vbs(fp)
                    fp.close
                #  get specific list
                with open(file) as fp:
                    list_name = parse_list_from_vbs(fp)
                    fp.close
                #  check all files under the list
                list = locate_child_node(root, list_name)
                if parse_files_from_list(list):
                    print ("\x1b[1;37;40mFILE: %s\x1b[0m \x1b[1;32;40m[clear]\x1b[0m" % file)
                else:
                    print ("\x1b[1;37;40mFILE: %s\x1b[0m \x1b[1;31;40m[error]\x1b[0m" % file)

main()
