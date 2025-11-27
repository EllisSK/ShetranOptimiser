from pathlib import Path
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2

from shetran_interaction import *
from results_analysis import *
from optimiser import ShetranProblem

def main():
    config = load_shetran_params(Path("temp/config.json"))

    algorithm = NSGA2(pop_size=20, n_offsprings=10, eliminate_duplicates=True)

    problem = ShetranProblem()

    res = minimize(problem, algorithm, verbose=True)

    print("Optimisation Complete.")
    print(f"Time taken: {res.exec_time} seconds")

if __name__ == "__main__":
    main()