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
        self.instructions = []
        
        self.vars = []
        
        self.callees = []
        self.callers = []

        self.input = {}
        self.output = {}
        self.arg = newarg
        self.ret = None

    def add_instruction(self, newinstr):
        self.instructions.append(newinstr)
    
    def add_return(self, newreturn):
        self.ret = newreturn

        # Init input and output tables to BOT
        for i in range(len(self.instructions)-1):
            self.input[i+1] = {}
            self.output[i+1] = {}
            for var in self.vars:
                self.input[i+1][var] = BOT
                self.output[i+1][var] = BOT

    def add_vars(self, newvars):
        self.vars = (self.vars + list(set(newvars) - set(self.vars)))

    def add_callee(self, new_callee):
        if not new_callee in self.callees:
            self.callees.append(new_callee)

    def add_caller(self, new_caller):
        if not new_caller in self.callers:
            self.callers.append(new_caller)

    def analysis(self):
        worklist = [1]
        while len(worklist) > 0 :
            index_instruction = worklist[0]
            worklist.pop(0)
            self.output[index_instruction] = self.instructions[index_instruction].flow_function(self.input[index_instruction])
            successors = self.instructions[index_instruction].succ(index_instruction,len(self.instructions))

            for succ in successors :
                if is_less_precise(self.output[index_instruction], self.input[succ]) :
                    for var in input[succ] :
                        self.input[succ][var] = join(self.input[succ][var], self.output[index_instruction][var])
                    worklist.append(succ)