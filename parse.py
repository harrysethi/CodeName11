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
        func_map, global_map, type_map, struct_map, global_access_map = {}, {}, {}, {}, {}

        for CU in dwarfinfo.iter_CUs():
            # DWARFInfo allows to iterate over the compile units contained in
            # the .debug_info section. CU is a CompileUnit object, with some
            # computed attributes (such as its offset in the section) and
            # a header which conforms to the DWARF standard. The access to
            top_DIE = CU.get_top_DIE()
            variables = {}
            members = {}
		

            die_info_rec_struct(top_DIE, struct_map, members, global_access_map)  
            # Display DIEs recursively starting with top_DIE
            die_info_rec(top_DIE, func_map, global_map, type_map, struct_map, variables, global_access_map)
	
	print func_map, global_map, type_map, global_access_map
        return func_map, global_map, type_map, global_access_map

def die_info_rec_struct(die, struct_map, members, global_access_map):
	if die.tag == "DW_TAG_structure_type":
		members = {}
		#struct_name = ''
		for attr in itervalues(die.attributes):
			if attr.name == 'DW_AT_name':
                		struct_name =  bytes2str(attr.value)

	elif die.tag == "DW_TAG_member":
		#var_name, loc = '',0
		for attr in itervalues(die.attributes):
			if attr.name == 'DW_AT_name':
                		var_name =  bytes2str(attr.value)
			if attr.name == 'DW_AT_data_member_location':
                		loc =  attr.value
		members[var_name] = (var_name, loc)

	for child in die.iter_children():
        	die_info_rec_struct(child, struct_map, members, global_access_map)

	if die.tag == "DW_TAG_structure_type":
        	struct_map[die.offset] = members

	#print struct_map

def die_info_rec(die, func_map, global_map, type_map, struct_map, variables, global_access_map):
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

    elif die.tag == "DW_TAG_variable" or die.tag == "DW_TAG_formal_parameter":
        global_flag = 0
        #var_name, offset, line, type_val = '',0,0,''
	offset_var = ''
        for attr in itervalues(die.attributes):
            if attr.name == 'DW_AT_name':
                var_name =  bytes2str(attr.value)
            elif attr.name == 'DW_AT_location':
                val = _location_list_extra(attr, die, ' ')
                #offset = int(val[val.index(':')+1:].strip()[:-1],16)
		offset_var = val[val.find(':')+1:val.find(')')].strip()
            elif attr.name == 'DW_AT_decl_line':
                line = attr.value
            elif attr.name == 'DW_AT_type':
                type_val = (attr.value + die.cu.cu_offset)
            elif attr.name == 'DW_AT_external':
                global_flag = 1

	if type_val in struct_map.keys():
	    struct_var_name = var_name
	    members = struct_map[type_val]
	    for member in members.keys():
		var_name = struct_var_name + "." + struct_map[type_val][member][0]
		struct_offset =	struct_map[type_val][member][1]
		addVariableInMap(global_flag, global_map, variables, offset_var, var_name, type_val, line, global_access_map, struct_offset)

	else:
	   addVariableInMap(global_flag, global_map, variables, offset_var, var_name, type_val, line, global_access_map, 0)
            
    elif die.tag == 'DW_TAG_base_type':
        #type_name, size = '',0
        for attr in itervalues(die.attributes):
            if attr.name == "DW_AT_name":
                type_name = bytes2str(attr.value)
            elif attr.name == 'DW_AT_byte_size':
                size = attr.value
                
        type_map[die.offset] = (type_name, size)

    for child in die.iter_children():
        die_info_rec(child, func_map, global_map, type_map, struct_map, variables, global_access_map)

            
    if die.tag == "DW_TAG_subprogram":
        #print (die.attributes)
        func_map[name] = variables     


def addVariableInMap(global_flag, global_map, variables, offset_var, var_name, type_val, line, global_access_map, struct_offset):
    if(offset_var == ''):
        return
    
    if global_flag == 1:
        global_map[int(offset_var,16)+struct_offset] = (var_name, type_val, line)
	global_access_map[var_name] = 1
    else:
        variables[int(offset_var)+struct_offset] = (var_name, type_val, line) 
	
