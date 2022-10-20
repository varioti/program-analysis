# Init operators and abstract values
op_num = ["+","-","*","/"]
op_bool = ["<","="]

TOP = "top"
Z = "zero"
P = "positive"
N = "negative"
BOT = "bottom"

# INSTRUCTIONS REPRESENTATION #########################################################

# Classes for the 5 types of instructions with : 
    # a flow function specific for each type
    # a get_vars function which returns all variables of the instruction

class Assign_Constant:
    """ 
    Represents var := cst 
    where cst belong to Z 
    """
    def __init__(self, newvar, newcst):
        self.var = newvar
        self.cst = newcst

    def __str__(self):
        return self.var+":="+str(self.cst)

    def flow_function(self, vars):
        out_vars = vars.copy()
        if self.cst == 0 :
            out_vars[self.var] = Z
        elif self.cst > 0 :
            out_vars[self.var] = P
        else :
            out_vars[self.var] = N
        return out_vars

    def succ(self, index, end):
        if index+1 < end :
            return [index+1]
        return []

    def get_vars(self):
        return [self.var]

class Assign_Operation:
    """ 
    Represents var := val1 <op> val2 
    where val1(2) is : - a variable if val1(2)IsVar is true
                       - a constant otherwise 
    """
    def __init__(self, newvar, newop):
        self.var = newvar
        
        # Find correct operator and split operation to obtain the 2 values
        correct_op = None
        i = 0
        while correct_op is None and i < len(op_num) :
            if op_num[i] in newop :
                correct_op = op_num[i]
                values = newop.split(correct_op)
            i += 1
         
        self.op = correct_op
        
        # Check if 1st value is constant or variable
        if values[0][0] == "-" or values[0].isnumeric() :
            self.val1 = int(values[0])
            self.val1IsVar = False
        else :
            self.val1 = values[0]
            self.val1IsVar = True

        # Check if 2nd value is constant or variable
        if values[1][0] == "-" or values[1].isnumeric() :
            self.val2 = int(values[1])
            self.val2IsVar = False
        else :
            self.val2 = values[1]
            self.val2IsVar = True

    def __str__(self):
        return self.var+":="+self.op

    def flow_function(self, vars):
        out_vars = vars.copy()
        # Compute abstract value of 1st value in the expression
        if not self.val1IsVar : # constant
            if self.val1 == 0 :
                abs_val1 = Z
            elif self.val1 < 0 :
                abs_val1 = N
            else :
                abs_val1 = P
        else : # variable (with already an abstract value)
            abs_val1 = vars[self.val1]

        # Compute abstract value of 2nd value in the expression
        if not self.val2IsVar : # constant
            if self.val2 == 0 :
                abs_val2 = Z
            elif self.val2 < 0 :
                abs_val2 = N
            else :
                abs_val2 = P
        else : # variable (with already an abstract value)
            abs_val2 = vars[self.val2]

        # Compute abstract value of the expression
        if self.op == "/" and abs_val2 == Z :
            out_vars[self.var] = BOT
        
        elif abs_val1 == Z and abs_val2 == Z :  
            out_vars[self.var] = Z
        
        elif self.op in ["*","/"] :
            if abs_val1 == Z :
                out_vars[self.var] = abs_val2
            elif abs_val2 == Z :
                out_vars[self.var] = abs_val1    
            elif abs_val1 == abs_val2 and abs_val1 in [N,P] : # if 
                out_vars[self.var] = P
            elif abs_val1 != abs_val2 and abs_val1 in [N,P] and abs_val2 in [N,P] :
                out_vars[self.var] = N
            else :
                out_vars[self.var] = TOP

        elif self.op == "+" :
            if abs_val1 == Z :
                out_vars[self.var] = abs_val2
            elif abs_val2 == Z :
                out_vars[self.var] = abs_val1
            else :
                out_vars[self.var] = join(abs_val1,abs_val2)
        else :
            if abs_val1 == Z :
                if abs_val2 == P :
                    out_vars[self.var] = N
                elif abs_val2 == N : 
                    out_vars[self.var] = P
            elif abs_val2 == Z :
                out_vars[self.var] = abs_val1
            elif abs_val1 == P and abs_val2 == N :
                out_vars[self.var] = P
            elif abs_val1 == N and abs_val2 == P :
                out_vars[self.var] = N
            else : 
                out_vars[self.var] = TOP

        return out_vars

    def succ(self, index, end):
        if index+1 < end :
            return [index+1]
        return []

    def get_vars(self):
        vars = [self.var]
        if self.val1IsVar :
            vars.append(self.val1)
        if self.val2IsVar :
            vars.append(self.val2)
        return vars

class Assign_Var:
    """ 
    Represents var1 := var
    where var1 and var2 are variables
    """
    def __init__(self, newvar1, newvar2):
        self.var1 = newvar1
        self.var2 = newvar2

    def __str__(self):
        return self.var1+":="+self.var2

    def flow_function(self, vars):
        out_vars = vars.copy()
        # Remplace abstract value of the 1st variable by the abstract value of the 2nd
        out_vars[self.var1] = out_vars[self.var2]
        return out_vars

    def succ(self, index, end):
        if index+1 < end :
            return [index+1]
        return []
    
    def get_vars(self):
        return [self.var1, self.var2]

class Branch:
    """ 
    Represents if val <bool op> 0 goto <goto> 
    where val is : - a variable if valIsVar is true
                   - a constant otherwise,
          <goto> is an instruction number 
    """
    def __init__(self, newcomp, newgoto):
        # Check if 1st value is constant or variable
        if newcomp[0] == "-" or newcomp.isnumeric() :
            self.val = int(newcomp[:-1])
            self.valIsVar = False
        else :
            self.val = newcomp[:-1]
            self.valIsVar = True

        self.op = newcomp[-1]
        self.goto = int(newgoto)

    def __str__(self):
        return "if"+self.comp+"0goto"+str(self.goto)

    def flow_function(self, vars):
        outvars = vars.copy()
        if self.valIsVar :
            outvars[self.val] = TOP
        return outvars

    def succ(self, index, end):
        return [index+1,self.goto]


    def get_vars(self):
        if self.valIsVar :
            return [self.val]
        return []

class Goto:
    """
    Represents goto <goto>
    where <goto> is an instruction number 
    """
    def __init__(self, newgoto):
        self.goto = newgoto

    def __str__(self):
        return "goto"+str(self.goto)

    def flow_function(self, vars):
        return vars.copy()

    def succ(self, index, end):
        return [self.goto]


    def get_vars(self):
        return []


class Instruction:
    """
    General class for an instruction which instanciate one of 5 specific instruction and uses its specific method
    """
    def __init__(self, str_instruction):
        # Remove spaces
        clean_str = str_instruction.replace(" ","") 

        # ASSIGNATION INSTRUCTION
        if ":=" in clean_str :
            tokenized_line = clean_str.split(":=")

            # CONSTANT
            if tokenized_line[1][0] == "-" or tokenized_line[1].isnumeric() : 
                self.instruction = Assign_Constant(tokenized_line[0], int(tokenized_line[1]))
            
            # OPERATION
            elif any(op in tokenized_line[1] for op in op_num) :
                self.instruction = Assign_Operation(tokenized_line[0], tokenized_line[1])

            # VAR
            else :
                self.instruction = Assign_Var(tokenized_line[0], tokenized_line[1])

        # BRANCH INSTRUCTION
        elif clean_str[0:2] == "if" :
            tokenized_line = clean_str[2:].split("0goto")
            self.instruction = Branch(tokenized_line[0], int(tokenized_line[1]))

        # GOTO INSTRUCTION
        else :
            self.instruction = Goto(int(clean_str[4:]))

    def __str__(self):
        return str(self.instruction)

    def flow_function(self, vars):
        return self.instruction.flow_function(vars)

    def succ(self, index, end):
        return self.instruction.succ(index, end)

    def get_vars(self):
        return self.instruction.get_vars()

# UTILS FUNCTIONS #####################################################################

def read_file(filename):
    """ Returns the w3a program in a list where each line is an element of the list """
    f = open(filename, "r")
    program = f.read().splitlines()
    f.close()
    return program

def read_program(program):
    """ Returns the program as a list of objects Instruction and the input table where all variables are initialized to BOTTOM """
    instructions = [None] # 0 added in order to have instruction 1 at position 1 in the list
    input = [{}]
    vars = []
    
    for line in program:
        i = Instruction(line)
        vars = (vars + list(set(i.get_vars()) - set(vars)))
        instructions.append(i)
    
    for i in range(len(instructions)-1):
        input.append({})
        for var in vars:
            input[i+1][var] = BOT

    return instructions, input

def join(x,y):
    """ Returns the abstract value of x JOIN y """
    if x == TOP or y == TOP :
        return TOP
    if x == y :
        return x
    if x != y and x in [P,N,Z] and y in [P,N,Z] :
        return TOP
    if x == BOT :
        return y
    if y == BOT :
        return x

def is_less_precise(output, input):
    """ Returns true if <output> is not more precise than <input>, false otherwise """
    is_more_precise = True
    for var in output.keys() :
        if input[var] != output[var] and ((output[var] in [Z,P,N] and input[var] == BOT) or (output[var] == TOP and input[var] in [Z,P,N])) :
            is_more_precise = False

    return not is_more_precise

# WORKLIST ALGORITHM ##################################################################

def worklist_algo(filename) :
    """ Applies Worklist algorithm to a program and returns the final input and output abstract values of all variables of the programm """
    program = read_file(filename)
    instructions, input = read_program(program)
    output = {}

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

# ANALYSIS ##################################################################

def analysis_div_by_zero(filename) :
    instructions,_ = read_program(read_file(filename))
    input,_ = worklist_algo(filename)
    
    # Filter division instructions
    div_instructions = {}
    for i in range(len(instructions)-1) :
        instr = instructions[i+1].instruction
        if isinstance(instr,Assign_Operation) and instr.op == "/" and instr.val2IsVar :
            
            if input[i+1][instr.val2] == Z :
                print("ERROR: DIV BY 0 (Line %i: denominator is 0)" % (i+1))

            if input[i+1][instr.val2] == TOP :
                print("INFO: DIV BY 0 (Line %i: denominator value unknown)" % (i+1))

# MAIN ###################################################################### 

filename = "codes/branch.w3a"
analysis_div_by_zero(filename)

# Show the input and the output tables
if True :
    print("--------------- INPUTS LIST ---------------")
    inp,out = worklist_algo(filename)
    num = 0
    for i in inp :
        print(str(num) + ": " + str(i))
        num += 1
    print("-------------- OUTPUTS LIST ---------------")
    for key in sorted(out.keys()) :
        print(str(key) + ": " + str(out[key]))