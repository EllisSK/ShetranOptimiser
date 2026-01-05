import sys
import os
import dill

import numpy as np

from argparse import ArgumentParser, Namespace
from pathlib import Path
from pymoo.optimize import minimize
from pymoo.algorithms.moo.rnsga3 import RNSGA3
from pymoo.operators.sampling.lhs import LHS
from pymoo.algorithms.moo.nsga2 import NSGA2, PM, SBX
from pymoo.termination import get_termination
from pymoo.parallelization.starmap import StarmapParallelization
from multiprocessing import cpu_count, Manager
from multiprocessing.pool import ThreadPool
from dotenv import set_key


from .settings import Settings, create_settings
from .shetran_interaction import load_shetran_params
from .optimiser import ShetranProblem, Checkpoint

def update_config(args: Namespace):
    if not os.path.exists(".env"):
        create_settings()
    
    if args.main_executable:
        set_key(".env", "SHETRAN_EXECUTABLE", str(args.main_executable))
    
    if args.prepare_executable:
        set_key(".env", "SHETRAN_PREPARE_EXECUTABLE", str(args.prepare_executable))

def setup_algorithm(args: Namespace, n_threads: int, problem: ShetranProblem):
    pop = 120
    print(pop)

    sampling = LHS()
    
    initial_pop_X = sampling.do(problem, pop).get("X") 

    best_solution = np.array([
        1.2380, 4.6126, 0.6087, 0.6724, 1.0643,
        0.3332, 4.0000, 0.0315, 0.4743, 3.8256,
        0.1124, 3.4263, 0.6450, 0.6500, 1.1787,
        2.4714, 18.5888, 2.3251, 0.2936, 8.1446,
        3.3083, 5.9628, 2.2146, 1.3907, 8.5690,
        1.3547, 3.4091, 1.9081, 0.9058, 16.0329,
        0.8258, 0.7821, 0.3851, 0.7120, 76.3240,
        0.9066, 0.2845, 30.8101, 0.0360, 1.7237,
        0.4430, 0.1258, 0.8839, 0.0057, 1.1211,
        0.9639, 0.2536, 0.0210, 0.0127, 1.2210,
        0.4708, 0.3484, 0.0292, 0.0118, 1.0188,
        0.1258, 0.0470, 7.6614, 0.0052, 1.3215,
        0.0384, 0.0011, 0.2110, 0.0916, 1.8059,
        0.4378, 0.1318, 0.0001, 0.0026, 1.1890
    ])

    initial_pop_X[0, :] = best_solution

    ref_points = np.array([[0.08, 0.08, 0.15]]) 

    return RNSGA3(
        ref_points=ref_points,
        pop_per_ref_point=pop,
        mu=0.05,
        sampling=initial_pop_X,
        n_offsprings=pop,
        eliminate_duplicates=True
    )

    #return NSGA2(pop_size=pop, n_offsprings=pop, eliminate_duplicates=True, crossover= SBX(eta=15), mutation=PM(eta=5))


def optimise(args: Namespace):
    env_settings = Settings()
    
    if not os.path.exists(".env"):
        create_settings()
        "Executables not set! Please use shetran-optimise config to set them"
        return

    if not env_settings.shetran_executable or not env_settings.shetran_prepare_executable:
        "Executables not set! Please use shetran-optimise config to set them"
        return

    debug_state = args.debug

    project_directory = Path(args.project)

    run_settings = {
        "base_project_directory": project_directory,
        "observed_data": project_directory / "observed.csv",
        "shetran_path": env_settings.shetran_executable,
        "preprocessor_path": env_settings.shetran_prepare_executable,
        "checkpoint_path": project_directory / "checkpoint.pkl",
        "debug": debug_state,
        "config_path": project_directory / "config.json"
    }

    config = load_shetran_params(run_settings["config_path"])

    run_settings["catchment_name"] = config["CatchmentDetails"]["CatchmentName"]

    with Manager() as manager:
        shared_lock = manager.Lock()

        n_threads = cpu_count()
        pool = ThreadPool(n_threads)
        runner = StarmapParallelization(pool.starmap)

        problem = ShetranProblem(
            config, run_settings, shared_lock, elementwise_runner=runner
        )

        if args.resume:
            print("Starting from saved state.")
            if os.path.exists(run_settings["checkpoint_path"]):
                with open(run_settings["checkpoint_path"], "rb") as file:
                    algorithm = dill.load(file)
                algorithm.problem.elementwise_runner = runner
                algorithm.problem.lock = shared_lock
            else:
                print("Could not find checkpoint file! Starting fresh run.")
                algorithm = setup_algorithm(args, n_threads, problem)
        else:
            print("Starting fresh run.")
            algorithm = setup_algorithm(args, n_threads, problem)

        res = minimize(
            problem,
            algorithm,
            termination=get_termination("n_gen", n_threads*8),
            verbose=True,
            callback=Checkpoint(run_settings["checkpoint_path"]),
            copy_algorithm=False,
        )

        pool.close()

        print("Optimisation Complete.")
        print(f"Time taken: {res.exec_time} seconds")