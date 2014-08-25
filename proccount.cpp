/* ---- This file is modified by Harinder Pal (2014MCS2123)  --- */
//
// This tool counts the number of times a routine is executed and 
// the number of instructions executed in a routine
//

#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include "pin.H"

FILE * trace;
ofstream outFile;
//string prev;
string operation = "";
string fn;

VOID RecordMemRead(VOID * ip, VOID * addr, string fn)
{
    //outFile << ip << " :R: " << addr;
    //operation = operation + (string)ip;
   outFile << ip << " :R: " << addr << endl;
	//fprintf(trace,"%p: R %p\n", ip, addr);
}

/*VOID GetBasePtr(ADDRINT reg)
{
    outFile << "reached" << reg << endl;
}*/

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr, string fn)
{
    //fprintf(trace,"%p: W %p\n", ip, addr);
    outFile << ip << " :W: " << addr << endl;
}

// Holds instruction count for a single procedure
/*typedef struct RtnCount
{
    string _name;
    string _image;
    ADDRINT _address;
    RTN _rtn;
    UINT64 _rtnCount;
    UINT64 _icount;
    struct RtnCount * _next;
} RTN_COUNT;*/

/*typedef struct RtnName
{
    string _name;
    string _op;
    struct RtnCount * _next;
} RTN_NAME;

RTN_NAME * RtnList = 0;*/



// Linked list of instruction counts for each routine
//RTN_COUNT * RtnList = 0;

// This function is called before every instruction is executed
/*VOID docount(UINT64 * counter)
{
    (*counter)++;
}*/

/*const char * StripPath(const char * path)
{
    const char * file = strrchr(path,'/');
    if (file)
        return file+1;
    else
        return path;
} */

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{	
	/*string current_prev = "None";
	if(RTN_Prev(rtn) != RTN_Invalid()) {
		current_prev = RTN_Name(RTN_Prev(rtn));
	}*/
	

	if(RTN_Name(rtn) == fn) {
		//prev = RTN_Name(rtn);
		//outFile << prev;
		//outFile << "Inside: " << RTN_Name(rtn) << endl;

		//fprintf(trace,"Hello: ");
		/*RTN_NAME * rn = new RTN_NAME;		
		rn->_name = RTN_Name(rtn);
		rn->_next = RtnList;
		RtnList = rn;*/

		RTN_Open(rtn);
		
		
		//string fn = RTN_Name(rtn);
		for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

		//RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)GetBasePtr, IARG_REG_VALUE, REG_STACK_PTR, IARG_END);
			UINT32 memOperands = INS_MemoryOperandCount(ins);

			for (UINT32 memOp = 0; memOp < memOperands; memOp++)
			{
				if (INS_MemoryOperandIsRead(ins, memOp))
				{
				    INS_InsertCall(
					ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
					IARG_INST_PTR,
					IARG_MEMORYOP_EA, memOp,
					IARG_END);
				}

				if (INS_MemoryOperandIsWritten(ins, memOp))
				{
				    INS_InsertCall(
					ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
					IARG_INST_PTR,
					IARG_MEMORYOP_EA, memOp, IARG_END);
				}
	
			}
		}

		

	  /*  // Allocate a counter for this routine
	    RTN_COUNT * rc = new RTN_COUNT;

	    // The RTN goes away when the image is unloaded, so save it now
	    // because we need it in the fini
	    rc->_name = RTN_Name(rtn);
	    rc->_image = StripPath(IMG_Name(SEC_Img(RTN_Sec(rtn))).c_str());
	    rc->_address = RTN_Address(rtn);
	    rc->_icount = 0;
	    rc->_rtnCount = 0;

	    // Add to list of routines
	    rc->_next = RtnList;
	    RtnList = rc;
		    
	    RTN_Open(rtn);
		    
	    // Insert a call at the entry point of a routine to increment the call count
	    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)docount, IARG_PTR, &(rc->_rtnCount), IARG_END);
	    
	    // For each instruction of the routine
	    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
	    {
		// Insert a call to docount to increment the instruction counter for this rtn
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_PTR, &(rc->_icount), IARG_END);
	    }

	    
	    RTN_Close(rtn); */
		RTN_Close(rtn);
	}
}

// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID *v)
{

	fprintf(trace, "#eof\n");
	fclose(trace);
	
	
	
    /*outFile << setw(23) << "Procedure" << " "
          << setw(15) << "Image" << " "
          << setw(18) << "Address" << " "
          << setw(12) << "Calls" << " "
          << setw(12) << "Instructions" << endl;

    for (RTN_COUNT * rc = RtnList; rc; rc = rc->_next)
    {
        if (rc->_icount > 0)
            outFile << setw(23) << rc->_name << " "
                  << setw(15) << rc->_image << " "
                  << setw(18) << hex << rc->_address << dec <<" "
                  << setw(12) << rc->_rtnCount << " "
                  << setw(12) << rc->_icount << endl;
    }*/

}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool counts the number of times a routine is executed" << endl;
    cerr << "and the number of instructions executed in a routine" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char * argv[])
{
	
    PIN_InitSymbols();

    outFile.open("myFile.out");

	trace = fopen("proccount.out", "w");

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
	fn = argv[argc-1];


	outFile << fn << endl;
    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
