from copy import deepcopy
from utils import *
from procedure import Procedure
from instructions import *

# Init filename to perform the analysis and show_tables
filename = "codes/branch.w3a"
show_tables = True # if True : output and input tables printed
                   # if False : not printed                       

# PARSING FUNCTIONS ###################################################################

def read_file(filename):
    """ Returns the w3a program in a list where each line is an element of the list """
    f = open(filename, "r")
    program = f.read().splitlines()
    f.close()
    return program

def read_program(program):
    """ Returns the program as a list of objects Instruction and the input table where all variables are initialized to BOTTOM """
    functions = {}
    
    current_program = None
    for i in range(len(program)):
        line = program[i].replace(" ","")

        if "procedure" == line[:9]:
            fnc_name = line[9:].split("(")[0]
            fnc_arg = line[9:].split("(")[1].split(")")[0]
            if len(fnc_arg) == 0 :
                functions[fnc_name] = Procedure(fnc_name)
            else :
                functions[fnc_name] = Procedure(fnc_name, fnc_arg)
            current_program = fnc_name

        elif "return" == line[:6]:
            functions[current_program].add_return(line[6:])

        elif "endprocedure" in line:
            current_program = None

        else :
            i = Instruction(line)
            functions[current_program].add_vars(i.get_vars())
            functions[current_program].add_instruction(i)

            if isinstance(i.instruction, Proc_Call):
                 functions[current_program].add_callee(i.instruction.proc_name)

    # Add callers in function (by using all functions callees)
    for f_name in functions.keys():
        for callee in functions[f_name].callees:
            functions[callee].add_caller(f_name)

    return functions


# WORKLIST ALGORITHM ##################################################################

def interprocedural_analysis(filename) :
    """ Applies Worklist algorithm to a program and returns the final input and output abstract values of all variables of the programm """
    program = read_file(filename)
    functions = read_program(program)

    # Init args and ret (TOP for main anf BOT for the rest)
    args = {}
    ret = {}
    for f_name in functions.keys():
        f = functions[f_name]
        if f.name == "main":
            initialize = {"arg":T,"ret":TOP}
        else:  
            initialize = {"arg":BOT,"ret":BOT}

        args[f.name] = []
        for _ in f.arg :
            args[f.name].append(initialize["arg"])

        ret[f.name] = []
        for _ in f.ret :
            ret[f.name].append(initialize["ret"])

    # Init wlp
    wlp = ["main"]

    # Main loop
    while len(wlp) > 0:
        p = functions[wlp[0]]
        wlp.pop(0)

        args_2 = deepcopy(args)
        ret_2 = deepcopy(ret)

        args, ret = p.analysis(args,ret)

        # Check procedures which are called by current function
        pcallees = p.callees
        for q in pcallees:
            if args[q] != args_2[q]:
                wlp.append(q)
        
        # Chech procedures which call current function
        if ret_2[p.name] != ret[p.name]:
            pcallers = p.callers
            for r in pcallers:
                wlp.append(r)

    return args, ret, functions


# ANALYSIS ##################################################################

def tainted_fct_call(filename):
    args,_,_ = interprocedural_analysis(filename)
    
    for fnc in args.keys():
        if fnc != "main" and args[fnc] == [T]:
            print(f"WARNING: function {fnc} called with a tainted parameter")


# MAIN ######################################################################
tainted_fct_call(filename)

# Show args and ret of all functions + output values of main function
if show_tables :
    args,ret,functions = interprocedural_analysis(filename)
    for fnc in args.keys():
        print_values = "\n" + fnc + ":\n" + "-" * (len(fnc)+1) + "\n"
        print_values += "| ARGS  |  RET  |\n|-------|-------|\n"
        
        if args[fnc] == []:
            print_values += "|   X   |"
        else:
            print_values = print_values + "| " + args[fnc][0] + " |"

        if ret[fnc] == []:
            print_values += "   X   |"
        else:
            print_values = print_values + " " + ret[fnc][0] + " |"

        print(print_values)

        print(f"\n{fnc} output:")
        output = functions[fnc].output
        for instruc in output.keys():
            print(f"\t{instruc}: {output[instruc]}")