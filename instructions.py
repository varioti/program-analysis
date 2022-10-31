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

    def init_tables(self):
        for i in range(len(self.instructions)-1):
            self.input.append({})
            for var in self.vars:
                self.input[i+1][var] = BOT

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
        if self.op == "/" and abs_val2 == Z : # div by 0
            out_vars[self.var] = BOT
        
        elif abs_val1 == Z and abs_val2 == Z : # mult, add and sub 0 and 0 = 0
            out_vars[self.var] = Z
        
        elif self.op in ["*","/"] :
            if abs_val1 == Z : # 0 * n and 0 / n = 0 
                out_vars[self.var] = abs_val2
            elif abs_val2 == Z : # n * 0 = 0 (n / 0 already covered)
                out_vars[self.var] = abs_val1    
            elif abs_val1 == abs_val2 and abs_val1 in [N,P] : # mult and div with same sign = positive 
                out_vars[self.var] = P
            elif abs_val1 != abs_val2 and abs_val1 in [N,P] and abs_val2 in [N,P] : # mult and div with different sign = negative
                out_vars[self.var] = N
            else : # otherwise => top
                out_vars[self.var] = TOP

        elif self.op == "+" :
            if abs_val1 == Z : # 0 + n = n
                out_vars[self.var] = abs_val2
            elif abs_val2 == Z : # n + 0 = n
                out_vars[self.var] = abs_val1
            else : # otherwise => join 2 values
                out_vars[self.var] = join(abs_val1,abs_val2)
        else : # substraction
            if abs_val1 == Z :
                if abs_val2 == P : # 0 - n = -n
                    out_vars[self.var] = N
                elif abs_val2 == N : # 0 - (-n) = n
                    out_vars[self.var] = P
            elif abs_val2 == Z : # n - 0 = n
                out_vars[self.var] = abs_val1
            elif abs_val1 == P and abs_val2 == N : # n - (-m) => pos
                out_vars[self.var] = P
            elif abs_val1 == N and abs_val2 == P :# (-n) - m => neg
                out_vars[self.var] = N
            else : # otherwise => TOPS
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

class Proc_Call:
    """
    Represents var := proc_name(proc_arg) 
    """
    def __init__(self, newvar, newname, newarg):
        self.var = newvar
        self.proc_name = newname
        self.proc_arg = newarg

    def __str__(self):
        return self.var + ":="+ self.proc_name +"(" +str(self.proc_arg)+")"

    def flow_function(self, vars):
        return vars.copy()

    def succ(self, index, end):
        return [self.goto]

    def get_vars(self):
        return [self.var, self.proc_arg]


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

    def flow_function(self, vars):
        return self.instruction.flow_function(vars)

    def succ(self, index, end):
        return self.instruction.succ(index, end)

    def get_vars(self):
        return self.instruction.get_vars()