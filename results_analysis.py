import pandas as pd

from pathlib import Path

def calculate_objective_function_metrics(observed_values: Path, simulated_values: Path) -> tuple:
    """
    Caculates 3 objective function metrics of a Shetran run.
    
    :param observed_values: Full path to observed flow values csv file location.
    :type observed_values: Path
    :param simulated_values: Full path to simulated flow values csv file location.
    :type simulated_values: Path
    """
    
    #Calculate KGE for general performance.

    #Calculate log(KGE) for low flow performance.

    #Calculate RMSE of flow duration curve.

    #Return (1-KGE, 1-log(KGE), FDC-RMSE)
    
    return ()