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
        if not newarg is None:
            self.vars.append(newarg)
        
        self.callees = []
        self.callers = []

        self.nb_instructions = 0
        self.instructions = {}

        self.input = {}
        self.output = {}

        self.arg = newarg
        self.ret = None

    def add_instruction(self, newinstr):
        self.nb_instructions+=1
        self.instructions[self.nb_instructions] = newinstr
    
    def add_return(self, newreturn):
        self.ret = newreturn

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

    def analysis(self):
        new_input = deepcopy(self.input)
        new_output = deepcopy(self.output)

        worklist = [1]

        while len(worklist) > 0 :
            print(worklist)
            index_instruction = worklist[0]
            worklist.pop(0)
            new_output[index_instruction] = self.instructions[index_instruction].flow_function(new_input[index_instruction])
            successors = self.instructions[index_instruction].succ(index_instruction,len(self.instructions))

            for succ in successors :
                if is_less_precise(new_output[index_instruction], new_input[succ]) :
                    for var in new_input[succ] :
                        new_input[succ][var] = join(new_input[succ][var], new_output[index_instruction][var])
                    worklist.append(succ)

        self.input = new_input
        self.output = new_output