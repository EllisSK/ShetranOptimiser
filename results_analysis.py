import math

import pandas as pd
import numpy as np

from pathlib import Path

def calculate_KGE(observed_values: pd.Series, simulated_values: pd.Series) -> float:
    """
    Calculates the Kling-Gupta efficiency for a set of observed and simulated values.
    
    :param observed_values: Pandas series of observed values.
    :type observed_values: pd.Series
    :param simulated_values: Pandas series of simulated values.
    :type simulated_values: pd.Series
    :return: Kling-Gupta efficiency.
    :rtype: float
    """
    if len(observed_values) != len(simulated_values):
        raise Exception("Series are not the same length!")

    r = np.corrcoef(simulated_values, observed_values)[0, 1]
    alpha = np.std(simulated_values) / np.std(observed_values)
    beta = np.mean(simulated_values) / np.mean(observed_values)

    return 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
    
def calculate_RMSE(observed_values: pd.Series, simulated_values: pd.Series) -> float:
    """
    Calculates the RMSE for a set of observed and simulated values.
    
    :param observed_values: Pandas series of observed values.
    :type observed_values: pd.Series
    :param simulated_values: Pandas series of simulated values.
    :type simulated_values: pd.Series
    :return: Root Mean Square Error.
    :rtype: float
    """
    if len(observed_values) != len(simulated_values):
        raise Exception("Series are not the same length!")
    
    squared_errors = (simulated_values - observed_values) ** 2

    mse = np.mean(squared_errors)

    return np.sqrt(mse)

def calculate_objective_function_metrics(observed_values: Path, simulated_values: Path) -> tuple:
    """
    Caculates 3 objective function metrics of a Shetran run.
    
    :param observed_values: Full path to observed flow values csv file location.
    :type observed_values: Path
    :param simulated_values: Full path to simulated flow values csv file location.
    :type simulated_values: Path
    """
    obs_df = pd.read_csv(
        observed_values,
        skiprows=20,
        usecols=[0,1],
        header=None,
        names=["Date", "ObservedFlow"],
        parse_dates=[0],
        index_col=0
    )

    sim_df = pd.read_csv(
        simulated_values,
        header=None,
        skiprows=1,
        names=["SimulatedFlow"]
    )
    
    kge = calculate_KGE(obs_df["ObservedFlow"], sim_df["SimulatedFlow"])

    obs_df["LogObservedFlow"] = np.log(obs_df["ObservedFlow"].clip(lower=0.01))
    sim_df["LogSimulatedFlow"] = np.log(sim_df["SimulatedFlow"].clip(lower=0.01))

    log_kge = calculate_KGE(obs_df["LogObservedFlow"], sim_df["LogSimulatedFlow"])

    fdc_rmse = calculate_RMSE(
        obs_df["ObservedFlow"].sort_values(ascending=False),
        sim_df["SimulatedFlow"].sort_values(ascending=False)
    )

    return (1-kge, 1-log_kge, fdc_rmse)