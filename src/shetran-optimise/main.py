import sys
import os
import dill

from pathlib import Path
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.parallelization.starmap import StarmapParallelization
from multiprocessing import cpu_count, Manager
from multiprocessing.pool import ThreadPool

from .shetran_interaction import *
from .results_analysis import *
from .optimiser import ShetranProblem, Checkpoint


def main():
    config = load_shetran_params(Path("temp/detailed_config.json"))

    settings = {
        "catchment_name": sys.argv[1],
        "base_project_directory": sys.argv[2],
        "observed_data": sys.argv[3],
        "shetran_path": sys.argv[4],
        "preprocessor_path": sys.argv[5],
    }

    checkpoint_path = "checkpoint.pkl"

    with Manager() as manager:
        shared_lock = manager.Lock()

        n_threads = max(1, cpu_count() - 4)
        pool = ThreadPool(n_threads)
        runner = StarmapParallelization(pool.starmap)

        problem = ShetranProblem(
            config, settings, shared_lock, elementwise_runner=runner
        )

        if os.path.exists(checkpoint_path):
            print("Starting from saved state.")
            with open(checkpoint_path, "rb") as file:
                algorithm = dill.load(file)
        else:
            print("Starting fresh run.")
            algorithm = NSGA2(pop_size=64, n_offsprings=64, eliminate_duplicates=True)

        res = minimize(
            problem,
            algorithm,
            termination=get_termination("n_gen", 256),
            verbose=True,
            callback=Checkpoint,
            copy_algorithm=False,
        )

        pool.close()

        print("Optimisation Complete.")
        print(f"Time taken: {res.exec_time} seconds")


if __name__ == "__main__":
    main()
