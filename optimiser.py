import numpy as np
import pandas as pd

from pymoo.core.problem import ElementwiseProblem

from shetran_interaction import *
from results_analysis import *

class ShetranProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__()
