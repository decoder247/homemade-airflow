"""
PSUEDOCODE:
- >>> workflow scheduler pipelines/

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
from modules import *


def get_files_in_folder(input_path_string: str = "", recursive: bool = False):
    return glob(input_path_string, recursive=recursive)


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
        "--runtime_min",
        type=int,
        required=False,
        default=None,
        help="Amount of time to run the program for",
    )

    return parser


if __name__ == "__main__":
    # Hardcoded
    ACCEPTED_PROGRAMS = ["scheduler"]
    RECURSIVENESS = True

    # Parses the first command first to determine program
    if len(argv) > 1 and argv[1] in ACCEPTED_PROGRAMS:
        program_mode = argv[1]
        if program_mode == "scheduler":
            argv.pop(1)  # TODO: Just prune for now
    elif len(argv) == 1:
        raise ValueError(f"Unexpected inputs - no inputs given")
    else:
        raise ValueError(
            f"Unexpected inputs, only accepting the following program modes {ACCEPTED_PROGRAMS}. Provided input - {argv[1:]}"
        )

    # Construct argparser object
    parser = construct_argparser()
    args = parser.parse_args()  # Parse sys.argv

    # Distribute arguments
    runtime_min = args.runtime_min
    workflow_input_paths = args.workflow_input_paths

    # Add to system path so it's findable, first remove any trailing '/' if present
    workflow_input_paths = [
        dirname(join(p, "dud_file.txt")) for p in workflow_input_paths
    ]
    [sys.path.append(p) for p in workflow_input_paths]

    # Check if folder exists for each path
    files_detected_per_path = dict()
    for input_path in workflow_input_paths:
        files_detected_per_path[input_path] = get_files_in_folder(
            join(input_path, "**"),  # Add wildcard for inputted paths
            recursive=RECURSIVENESS,
        )

    # For each input folder path, do
    # take only filename, replace to '.' convention for importing, and then take only .py files
    for input_path, files_list in files_detected_per_path.items():
        basename_list = [
            f.replace(input_path, "", 1).replace(sep, ".")[1:-3]
            for f in files_list
            if splitext(f)[-1] == ".py"
        ]  # Replace only first instance
        files_detected_per_path[input_path] = basename_list

    # Print out filepaths
    print(f"Here are the python files present in the specified paths:")
    print(json.dumps(files_detected_per_path, indent=4, sort_keys=True))

    for input_path, files_list in files_detected_per_path.items():
        for file_path in files_list:
            # TODO: DEBUG, production should run all python files
            if "modules" in file_path:
                modules = import_module(file_path)
            elif "example_job" in file_path:
                job = import_module(file_path)

    # Test running the pipeline defined in job
    job.pipeline.print_name()

    # Run watchdog
    w = modules.Watcher(
        "/Users/iliono/My Drive/Homefiles/repos-mac/homemade-airflow-ivanliono/src"
    )
    w.run()

    # TODO: Remaining
    """
    - Parse cron string
    - Implement scheduling logic
    """
