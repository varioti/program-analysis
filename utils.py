# Init operators and abstract values
op_num = ["+","-","*","/"]
op_bool = ["<","="]

TOP = "top"
T = "taint"
C = "clean"
BOT = "bottom" 

def join(x,y):
    """ Returns the abstract value of x JOIN y """
    if x == TOP or y == TOP :
        return TOP
    if x == y :
        return x
    if x != y and x in [T,C] and y in [T,C] :
        return TOP
    if x == BOT :
        return y
    if y == BOT :
        return x

def is_less_precise(output, input):
    """ Returns true if <output> is not more precise than <input>, false otherwise """
    is_more_precise = True
    for var in output.keys() :
        if input[var] != output[var] and ((output[var] in [T,C] and input[var] == BOT) or (output[var] == TOP and input[var] in [T,C])) :
            is_more_precise = False

    return not is_more_precise