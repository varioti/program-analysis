from copy import deepcopy
from utils import *

# INSTRUCTIONS REPRESENTATION #########################################################

# Classes for the 6 types of instructions with : 
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
        out_vars = vars
        out_vars[self.var] = C
        return out_vars

    def succ(self, index, end):
        if index+1 <= end :
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
        out_vars = vars
        # Compute abstract value of 1st value in the expression
        if not self.val1IsVar : # constant is clean
            abs_val1 = C
        else : # variable (with already an abstract value)
            abs_val1 = vars[self.val1]

        # Compute abstract value of 2nd value in the expression
        if not self.val2IsVar : # constant
            abs_val2 = C
        else : # variable (with already an abstract value)
            abs_val2 = vars[self.val2]

        # Compute abstract value of the expression
        if abs_val1 == abs_val2 and abs_val1 == C:
            out_vars[self.var] = C
        elif abs_val1 == T or abs_val2 == T :
            out_vars[self.var] = T
        else :
            out_vars[self.var] = TOP

        return out_vars

    def succ(self, index, end):
        if index+1 <= end :
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
        out_vars = vars
        # Remplace abstract value of the 1st variable by the abstract value of the 2nd
        out_vars[self.var1] = out_vars[self.var2]
        return out_vars

    def succ(self, index, end):
        if index+1 <= end :
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
        return deepcopy(vars)

    def succ(self, index, end):
        if self.goto <= end:
            return [index+1,self.goto]
        return [index+1]


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
        return vars

    def succ(self, index, end):
        if self.goto <= end:
            return [self.goto]
        return []

    def get_vars(self):
        return []

class Proc_Call:
    """
    Represents var := proc_name(proc_arg) 
    """
    def __init__(self, newvar, newname, newarg=None):
        self.var = newvar
        self.proc_name = newname
        self.proc_arg = newarg

    def __str__(self):
        return self.var + ":="+ self.proc_name +"(" +str(self.proc_arg)+")"

    def flow_function(self, vars, args, ret):
        new_arg = vars[self.proc_arg]
        old_arg = args[self.proc_name][0]
        args[self.proc_name][0] = join(new_arg, old_arg)
        vars[self.var] = ret[self.proc_name][0]

        return vars, args, ret

    def succ(self, index, end):
        if index+1 <= end :
            return [index+1]
        return []

    def get_vars(self):
        vars = [self.var]
        if not self.proc_arg is None:
            vars.append(self.proc_arg)
        return vars


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
            
            # PROCEDURE CALL
            elif "(" in tokenized_line[1] :
                proc_name = tokenized_line[1].split("(")[0]
                proc_arg = tokenized_line[1].split("(")[1][:-1]
                self.instruction = Proc_Call(tokenized_line[0], proc_name, proc_arg)
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

    def flow_function(self, vars, args, ret):
        if isinstance(self.instruction,Proc_Call):
            return self.instruction.flow_function(vars, args, ret)
        else:    
            return self.instruction.flow_function(vars), args, ret

    def succ(self, index, end):
        return self.instruction.succ(index, end)

    def get_vars(self):
        return self.instruction.get_vars()