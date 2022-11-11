from copy import deepcopy
from utils import *
from instructions import *

# PROCEDURES REPRESENTATION ##########################################################
class Procedure:
    """
    Represents a procedure :
        procedure <name>(<arg>):
            <instructions>
            return <ret>
        end procedure
    """
    def __init__(self, newname, newarg=None):
        self.name = newname
        
        self.vars = []
        
        self.callees = []
        self.callers = []

        self.nb_instructions = 0
        self.instructions = {}

        self.input = {}
        self.output = {}

        self.arg = []

        self.ret = []

        if not newarg is None:
            self.arg.append(newarg)
            self.vars.append(newarg)

    def add_instruction(self, newinstr):
        self.nb_instructions+=1
        self.instructions[self.nb_instructions] = newinstr
    
    def add_return(self, newreturn):
        self.ret.append(newreturn)

    def init_input_output(self):
        # Init input and output tables to BOT
        for i in range(self.nb_instructions):
            self.input[i+1] = {}
            self.output[i+1] = {}
            for var in self.vars:
                self.input[i+1][var] = BOT
                self.output[i+1][var] = BOT

    def add_vars(self, newvars):
        self.vars = list(dict.fromkeys(self.vars+newvars))

    def add_callee(self, new_callee):
            self.callees.append(new_callee)

    def add_caller(self, new_caller):
            self.callers.append(new_caller)

    def analysis(self, args, ret):
        # Function with only a return instruction
        if len(self.instructions) == 0:
            if len(self.arg) > 0 and self.arg[0] == self.ret[0]:
                ret[self.name][0] = join(ret[self.name][0],args[self.name][0])
            else:
                ret[self.name][0] = TOP
            return args, ret

        # But init the new value of arg in the 1st input
        if len(self.arg) > 0 :
            self.input[1][self.arg[0]] = args[self.name][0]

        # Worklist algo
        worklist = [1]
        while len(worklist) > 0 :

            index_instruction = worklist[0]
            worklist.pop(0)

            result, args, ret = self.instructions[index_instruction].flow_function(self.input[index_instruction], args, ret)
            self.output[index_instruction] = result

            successors = self.instructions[index_instruction].succ(index_instruction,self.nb_instructions)
            for s in successors :
                if is_less_precise(self.output[index_instruction], self.input[s]) : # Avoid infinite loop
                    for var in self.input[s] :
                        self.input[s][var] = join(self.input[s][var], self.output[index_instruction][var])
                    worklist.append(s)
        
        # Update return abstract value for this procedure
        if len(self.ret) > 0 :
            old_ret = ret[self.name][0]
            new_ret = self.output[self.nb_instructions][self.ret[0]]
            ret[self.name][0] = join(old_ret, new_ret)

        return args, ret