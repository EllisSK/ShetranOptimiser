import sys
import os
import dill

from argparse import ArgumentParser, Namespace
from pathlib import Path
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
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

def setup_algorithm(args: Namespace):
    return NSGA2(pop_size=12, n_offsprings=12, eliminate_duplicates=True)


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

        n_threads = max(1, cpu_count() - 2)
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
                algorithm = setup_algorithm(args)
        else:
            print("Starting fresh run.")
            algorithm = setup_algorithm(args)

        res = minimize(
            problem,
            algorithm,
            termination=get_termination("n_gen", 3),
            verbose=True,
            callback=Checkpoint(run_settings["checkpoint_path"]),
            copy_algorithm=False,
        )

        pool.close()

        print("Optimisation Complete.")
        if type(res.exec_time) is int:
            print(f"Time taken: {res.exec_time / 3600} hours")
        else:
            print(f"Time taken: {res.exec_time} seconds")