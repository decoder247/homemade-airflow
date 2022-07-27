"""
PSUEDOCODE:
>>> workflow scheduler pipelines/
>>> python -u "/Users/iliono/My Drive/Homefiles/repos-mac/homemade-airflow-ivanliono/src/workflow.py" scheduler '/Users/iliono/My Drive/Homefiles/repos-mac/homemade-airflow-ivanliono/dags'

* Takes in the inputted path and continuously monitors for new files, outputs string if so based on filename
* Adds it to a queue

LATER
===
* Parses python file and detects for any called pipeline objects
"""
import json
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, RawTextHelpFormatter
from glob import glob
from importlib import import_module
from os import sep
from os.path import basename, dirname, join, split, splitext
from sys import argv
from utils import *
from modules import *
from config import Config


def construct_argparser() -> ArgumentParser:
    """ """
    # Create parser object
    parser = ArgumentParser(
        prog="",
        description="",
        formatter_class=RawTextHelpFormatter,
    )

    # Add positional arguments
    parser.add_argument(
        "workflow_input_paths",
        metavar="PATH",
        type=str,
        nargs="+",
        help="Takes in paths where the job definitions reside",
    )

    # TODO: Add optional arguments
    parser.add_argument(
        "--runtime_minutes",
        type=int,
        required=False,
        default=None,
        help="Amount of time to run the program for",
    )

    return parser


if __name__ == "__main__":
    # Parses the first command first to determine program
    if len(argv) > 1 and argv[1] in Config.ACCEPTED_PROGRAMS:
        program_mode = argv[1]
        if program_mode == "scheduler":
            argv.pop(1)  # TODO: Just prune for now
    elif len(argv) == 1:
        raise ValueError(f"Unexpected inputs - no inputs given")
    else:
        raise ValueError(
            f"Unexpected inputs, only accepting the following program modes {Config.ACCEPTED_PROGRAMS}. Provided input - {argv[1:]}"
        )

    # Construct argparser object
    parser = construct_argparser()
    args = parser.parse_args()  # Parse sys.argv

    # Distribute arguments
    runtime_minutes = args.runtime_minutes
    workflow_input_paths = args.workflow_input_paths

    # Create orchestrator
    orchid = Orchestrator(workflow_input_paths, runtime_minutes, silent=False)

    # Execute orchestrator
    orchid.execute()
