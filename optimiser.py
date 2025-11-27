import numpy as np
import pandas as pd

from pymoo.core.problem import ElementwiseProblem

from shetran_interaction import *
from results_analysis import *

class ShetranProblem(ElementwiseProblem):
    def __init__(self, simulation_data: Path, observed_data: Path, config: dict, settings: dict):
        self.settings = settings
        self.observed_path = observed_data
        self.data_path = simulation_data
        
        params_to_optimise = []
        
        for table_name, rows in config.items():
            for row_id, columns in rows.items():
                for col_name, details in columns.items():
                    row_str = str(row_id).replace('(', '').replace(')', '')
                    param_name = f"{table_name} [ID:{row_str}] - {col_name}"
                    params_to_optimise.append({
                        "name": param_name,
                        "table": table_name,
                        "row_id": row_id,
                        "col_name": col_name,
                        "bounds": details["bounds"]
                    })

        self.pto = params_to_optimise

        xl = np.array([p["bounds"][0] for p in self.pto])
        xu = np.array([p["bounds"][1] for p in self.pto])

        super().__init__(
            n_var=len(self.pto), 
            n_obj=3, 
            n_constr=0, 
            xl=xl, 
            xu=xu)
