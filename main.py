from taint_analysis import tainted_fct_call, interprocedural_analysis

# Init filename to perform the analysis and show_tables
filenames = ["codes/double.w3a", "codes/multi_calls.w3a", "codes/recursion.w3a"]
show_tables = True # if True : output and input tables printed
                   # if False : not printed  

# MAIN ######################################################################
for filename in filenames:
    print(f"\n################################ {filename} ################################\n")
    tainted_fct_call(filename)

    # Show args and ret of all functions + output values of main function
    if show_tables :
        args,ret,functions = interprocedural_analysis(filename)
        for fnc in args.keys():
            print_values = "\n" + fnc + ":\n" + "-" * (len(fnc)+1) + "\n"
            print_values += "|  ARGS  |  RET   |\n|--------|--------|\n"
            
            if args[fnc] == []:
                print_values += "|   X    |"
            else:
                print_values = print_values + "| " + args[fnc][0] + " |"

            if ret[fnc] == []:
                print_values += "   X    |"
            else:
                print_values = print_values + " " + ret[fnc][0] + " |"

            print(print_values)

        print(f"\n-> main output:")
        output = functions["main"].output
        for instruc in output.keys():
            print(f"\t{instruc}: {output[instruc]}")

        print("\n")