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

    def end_procedure(self):
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
        if not new_callee in self.callees:
            self.callees.append(new_callee)

    def add_caller(self, new_caller):
        if not new_caller in self.callers:
            self.callers.append(new_caller)

    def analysis(self, args, ret):
        # Init input and output list to BOT
        self.end_procedure()

        # But analyze with new value of arg
        if len(self.arg) > 0 :
            self.input[self.arg[0]] = args[self.name][0]

        # Worklist algo
        worklist = [1]
        while len(worklist) > 0 :

            index_instruction = worklist[0]
            worklist.pop(0)

            result, args, ret = self.instructions[index_instruction].flow_function(self.input[index_instruction], args, ret)
            self.output[index_instruction] = result

            successors = self.instructions[index_instruction].succ(index_instruction,self.nb_instructions)
            for succ in successors :
                if is_less_precise(self.output[index_instruction], self.input[succ]) : # Avoid infinite loop
                    for var in self.input[succ] :
                        self.input[succ][var] = join(self.input[succ][var], self.output[index_instruction][var])
                    worklist.append(succ)
        
        # Update return abstract value for this procedure
        if len(self.ret) > 0 :
            ret[self.name][0] = self.output[self.nb_instructions][self.ret[0]]

        return args, ret