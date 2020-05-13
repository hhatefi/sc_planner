import sys, traceback

from lib.parser import Parser
from lib.supply_chain import SupplyChain
from lib.solver import PlanningSolver

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("[ERR] Invalid usage.")
        print("\n\nUsage: PROG <model> [<lp_file>]")
        print("\t<model> contains the supply chain description")
        print("\t<lp_file> if given, stores the LP")
        exit(1)
    model_fname=sys.argv[1]
    lp_file=sys.argv[2] if len(sys.argv)==3 else None
    try:
        par=Parser(model_fname)
        stmts=par.parse()
        supp_chain=SupplyChain(stmts)
        solver=PlanningSolver(supp_chain)
        solver.solve()
        print(solver)
        if lp_file:
            solver.write_lp(lp_file)
    except Exception as e:
        print(f"[ERR] Planning failed.\nReason:\n")
        print("="*100)
        traceback.print_exc()
        exit(2)
    exit(0)
