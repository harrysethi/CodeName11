import sys
from elftools.common.py3compat import (bytes2str, itervalues)
from elftools.dwarf.descriptions import _location_list_extra

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.elf.elffile import ELFFile


def process_file(filename):
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return {}, {}

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()
        func_map, global_map, type_map = {}, {}, {}

        for CU in dwarfinfo.iter_CUs():
            # DWARFInfo allows to iterate over the compile units contained in
            # the .debug_info section. CU is a CompileUnit object, with some
            # computed attributes (such as its offset in the section) and
            # a header which conforms to the DWARF standard. The access to
            top_DIE = CU.get_top_DIE()
            variables = {}
            
            # Display DIEs recursively starting with top_DIE
            die_info_rec(top_DIE, func_map, global_map, type_map, variables)

        return func_map, global_map, type_map        


def die_info_rec(die, func_map, global_map, type_map, variables):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    name = ''
    if die.tag == "DW_TAG_subprogram":
        variables = {}
        #print (die.attributes)
        for attr in itervalues(die.attributes):
            if attr.name == 'DW_AT_name':
                name = bytes2str(attr.value)

    elif die.tag == "DW_TAG_variable":
        global_flag = 0
        var_name, offset, line, type_val = '',0,0,''
        for attr in itervalues(die.attributes):
            if attr.name == 'DW_AT_name':
                var_name =  bytes2str(attr.value)
            elif attr.name == 'DW_AT_location':
                val = _location_list_extra(attr, die, ' ')
                offset = int(val[val.index(':')+1:].strip()[:-1],16)
            elif attr.name == 'DW_AT_decl_line':
                line = attr.value
            elif attr.name == 'DW_AT_type':
                type_val = (attr.value + die.cu.cu_offset)
            elif attr.name == 'DW_AT_external':
                global_flag = 1

        if global_flag == 1:
            global_map[offset] = (var_name, type_val, line)

        else:
            variables[offset + 12] = (var_name, type_val, line)
            
    elif die.tag == 'DW_TAG_base_type':
        type_name, size = '',0
        for attr in itervalues(die.attributes):
            if attr.name == "DW_AT_name":
                type_name = bytes2str(attr.value)
            elif attr.name == 'DW_AT_byte_size':
                size = attr.value
                
        type_map[die.offset] = (type_name, size)

    for child in die.iter_children():
        die_info_rec(child, func_map, global_map, type_map, variables)

            
    if die.tag == "DW_TAG_subprogram":
        #print (die.attributes)
        func_map[name] = variables       

