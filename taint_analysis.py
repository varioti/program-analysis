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
        print(line)
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
            functions[current_program].end_procedure()
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

def worklist_algo(filename) :
    """ Applies Worklist algorithm to a program and returns the final input and output abstract values of all variables of the programm """
    program = read_file(filename)
    functions = read_program(program)

    # Init args and ret
    args = {}
    ret = {}
    for f_name in functions.keys():
        f = functions[f_name]
        if f.name == "main":
            initialize = TOP
        else:  
            initialize = BOT

        args[f.name] = {}
        for a in f.arg :
            args[f.name][a] = initialize

        ret[f.name] = {}
        for r in f.ret :
            ret[f.name][r] = initialize

    # Init wlp
    wlp = ["main"]

    # Main loop
    while len(wlp) > 0:
        p = functions[wlp[0]]
        wlp.pop(0)

        args_2 = args.copy()
        ret_2 = ret.copy()

        p.analysis()

        callees = p.callees
        for q in callees:
            if args[q] != args_2[q]:
                wlp.append(q)
        
        if ret_2[p.name] != ret[p.name]:
            callers = p.callers
            for r in callers:
                wlp.append(r)


worklist_algo(filename)

"""
    worklist = [1]
    while len(worklist) > 0 :
        index_instruction = worklist[0]
        worklist.pop(0)
        output[index_instruction] = instructions[index_instruction].flow_function(input[index_instruction])
        successors = instructions[index_instruction].succ(index_instruction,len(instructions))

        for succ in successors :
            if is_less_precise(output[index_instruction], input[succ]) :
                for var in input[succ] :
                    input[succ][var] = join(input[succ][var], output[index_instruction][var])
                worklist.append(succ)

    return input, output
"""

# ANALYSIS ##################################################################

"""
def analysis_div_by_zero(filename) :
    instructions,_ = read_program(read_file(filename))
    input,_ = worklist_algo(filename)
    
    for i in range(len(instructions)-1) :
        instr = instructions[i+1].instruction
        # Check if instruction is a division operation
        if isinstance(instr,Assign_Operation) and instr.op == "/" and instr.val2IsVar :
            
            # Denominator is 0 => ERROR
            if input[i+1][instr.val2] == Z :
                print("ERROR: DIV BY 0 (Line %i: denominator is 0)" % (i+1))

            # Analysis doesn't know denominator value (could be 0 or sth else) => WARNING
            if input[i+1][instr.val2] == TOP :
                print("INFO: DIV BY 0 (Line %i: denominator value unknown)" % (i+1))

# MAIN ###################################################################### 

analysis_div_by_zero(filename)

# Show the input and the output tables
if show_tables :
    print("--------------- INPUTS LIST ---------------")
    inp,out = worklist_algo(filename)
    num = 0
    for i in inp :
        print(str(num) + ": " + str(i))
        num += 1
    print("-------------- OUTPUTS LIST ---------------")
    for key in sorted(out.keys()) :
        print(str(key) + ": " + str(out[key]))
"""