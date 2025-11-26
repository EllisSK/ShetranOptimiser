from pathlib import Path

from shetran_interaction import *
from results_analysis import *

def main():
    config = load_shetran_params(Path("temp/config.json"))


if __name__ == "__main__":
    main()
