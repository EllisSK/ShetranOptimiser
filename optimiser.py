import uuid
import os
import shutil
import multiprocessing
import time
import copy

import numpy as np
import pandas as pd

from pymoo.core.problem import ElementwiseProblem
from pymoo.core.callback import Callback

from shetran_interaction import *
from results_analysis import *

class ShetranProblem(ElementwiseProblem):
    def __init__(self, config: dict, settings: dict, lock, **kwargs):
        self.settings = settings

        self.base_dir = Path(f"{self.settings["base_project_directory"]}")
        self.master_xml = self.base_dir / f"{self.settings["catchment_name"]}_Library_File.xml"
        self.preprocessor = Path(self.settings["preprocessor_path"])
        self.shetran = Path(self.settings["shetran_path"])
        self.observed = self.base_dir / f"{self.settings["observed_data"]}"
        self.log = self.base_dir / "log.csv"
        self.lock = lock
        self.master_dict = read_xml_file(self.master_xml)
        self.tocopy = self.base_dir / "tocopy"
        
        params_to_optimise = []
        
        for section, s_list in config.items():
            for row in s_list:
                for param, bounds in row["Parameters"].items():
                    p = {}
                    descriptor_item = list(row["Descriptors"].items())[0]
                    p["name"] = f"{descriptor_item[0]}{descriptor_item[1]}{param}"
                    p["param_name"] = param
                    p["bounds"] = bounds
                    p["Section"] = section
                    p["Descriptors"] = row["Descriptors"]
                    params_to_optimise.append(p)

        self.pto = params_to_optimise

        param_names = [p["name"] for p in self.pto]
        objective_fn_names = ["1-KGE","1-LogKGE","RMSE"]
        header = ["Timestamp", "Run_ID"] + param_names + objective_fn_names

        with open(self.log, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

        xl = np.array([p["bounds"][0] for p in self.pto])
        xu = np.array([p["bounds"][1] for p in self.pto])

        super().__init__(
            n_var=len(self.pto), 
            n_obj=3, 
            n_constr=0, 
            xl=xl, 
            xu=xu,
            **kwargs
            )
        
    def _evaluate(self, x, out, *args, **kwargs):
        run_id = uuid.uuid4().hex[:8]

        run_dir = self.base_dir / "runs" / f"run_{run_id}"

        run_xml = run_dir / f"{self.settings["catchment_name"]}_Library_File.xml"
        rundata = run_dir / f"rundata_{self.settings["catchment_name"]}.txt"
        run_output = run_dir / f"output_{self.settings["catchment_name"]}_discharge_sim_regulartimestep.txt"
        run_help = run_dir / "helpmessages"

        objectives = [1e10, 1e10, 1e10]

        try:
            os.makedirs(run_dir, exist_ok=True)
            os.makedirs(run_help, exist_ok=True)

            shutil.copytree(self.tocopy, run_dir, dirs_exist_ok=True)

            update_dict = copy.deepcopy(self.master_dict)

            for i, prop in enumerate(self.pto):
                section = prop["Section"]
                descriptors = prop["Descriptors"]
                param_key = prop["param_name"]

                for row in update_dict[section]:
                    if row["Descriptors"] == descriptors:
                        row["Parameters"][param_key] = x[i]
                        break

            modify_xml_file(run_xml, update_dict)

            run_preprocessor(self.preprocessor, run_xml)

            run_shetran(self.shetran, rundata)
            with self.lock:
                objectives = calculate_objective_function_metrics(self.observed, run_output)
            out["F"] = list(objectives)

        except:
            out["F"] = objectives
        finally:
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                log_row = [timestamp, run_id] + list(x) + list(objectives)
                with self.lock:
                    with open(self.log, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(log_row)
                
                print(f"Logging successful for {run_id}!")     

            except Exception as log_err:
                print(f"Logging failed for {run_id}: {log_err}")
           
#            if os.path.exists(run_dir):
#                shutil.rmtree(run_dir, ignore_errors=True)

class MyCallback(Callback):
    def __init__(self):
        super().__init__()

    def notify(self, algorithm):
        print(f"Running Generation Number {algorithm.n_gen}")