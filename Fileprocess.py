import parse
from subprocess import call

def process(filename):

    func_map, global_map, type_map = parse.process_file(filename)

    access_map = {}
    
    comm_base = '../../../pin -t obj-intel64/proccount.so -- tempp/a.out '
    for key in func_map.keys():
        comm = comm_base + key
	print comm
        #call(comm)

        f = open("myFile.out", "r")
        f.readline()
        ebp = int(f.readline().split()[-1], 16)
        for line in f.readlines():
            address = int(line.split()[-1], 16)
            if address in global_map.keys():
                name = global_map[address][0]
                if name in access_map.keys():
                    access_map[name] += 1
                else:
                    access_map[name] = 1    
            else:
                offset = address - ebp - 16

                if offset in func_map[key].keys():
                    var_name = func_map[key][offset][0]
                    if var_name in access_map.keys():
                        access_map[var_name] += 1
                    else:
                        access_map[var_name] = 1

        f.close()
    return access_map
