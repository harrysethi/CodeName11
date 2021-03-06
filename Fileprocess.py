import parse
from subprocess import call

def process(filename):

    func_map, global_map, type_map, global_access_map = parse.process_file(filename)

    access_map = {}
    
    comm_base = '../../../pin -t obj-intel64/proccount.so -- ./a.out '
    for key in func_map.keys():
	inside_fn_map = {}
        comm = (comm_base + key).split()
	print comm
        call(comm)

        f = open("myFile.out", "r")
        f.readline()
	try:
            ebp = int(f.readline().split()[-1], 16)
	except IndexError:
	    continue
        for line in f.readlines():
            address = int(line.split()[-1], 16)
            if address in global_map.keys():
		#print "reached "
                name = global_map[address][0]
                global_access_map[name] += 1
            else:
                offset = address - ebp - 16
		print offset

                if offset in func_map[key].keys():
		    var_loc = func_map[key][offset][2]
                    var_name = func_map[key][offset][0] + "_l" + str(var_loc)
                    if var_name in inside_fn_map.keys():
                        inside_fn_map[var_name] += 1
                    else:
                        inside_fn_map[var_name] = 1

	access_map[key] = inside_fn_map
        f.close()

    access_map["Global"] = global_access_map
    
    print 'Printing Access Informaton:'
    print '---------------------------\n\n'
    for i in access_map.keys():
        print i + ':\n\n'
        for val in access_map[i].keys():
            print str(val) + ' : ' + str(access_map[i][val])

        print '\n\n'
