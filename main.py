from pathlib import Path
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2

from shetran_interaction import *
from results_analysis import *
from optimiser import ShetranProblem

def main():
    config = load_shetran_params(Path("temp/config.json"))

    algorithm = NSGA2()

    problem = ShetranProblem(config)

    res = minimize(problem)

if __name__ == "__main__":
    main()