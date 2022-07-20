import json
import sys
import time
from importlib import import_module
from inspect import isclass
from os import sep
from os.path import dirname, join, splitext

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import Config
from models import *
from modules import *
from utils import *


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == "created" and not Handler.check_if_ignored_file(
            event.src_path
        ):
            # Take any action here when a file is first created.
            print(f"Received created event - {event.src_path}.")

        elif event.event_type == "modified" and not Handler.check_if_ignored_file(
            event.src_path
        ):
            # Taken any action here when a file is modified.
            print(f"Received modified event - {event.src_path}.")

    @staticmethod
    def check_if_ignored_file(input_path: str):
        ignore_file_flag = True

        for watched_extension in Config.WATCHED_FILE_EXTENSIONS:
            if splitext(input_path)[-1] == watched_extension:
                ignore_file_flag = False
                break

        return ignore_file_flag


class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Watchdog Error!!")

        self.observer.join()


class Orchestrator:
    """
    Main orchestrator method
    """

    def __init__(
        self,
        workflow_input_paths: list,
        runtime_minutes: int = None,
        silent: bool = False,
    ):
        # Unpack arguments!!
        self.runtime_minutes = runtime_minutes
        self.files_detected_per_path = dict()
        self.pipeline_objects_per_path = dict()
        self.scheduler = Scheduling()

        # first Remove any trailing '/' if present
        workflow_input_paths = [dirname(join(p, "")) for p in workflow_input_paths]
        workflow_input_paths = workflow_input_paths

        # Add to system path so it's findable
        self.add_to_system_path(workflow_input_paths)

        # Check if folder exists for each path
        for input_path in workflow_input_paths:
            self.files_detected_per_path[input_path] = get_files_in_folder(
                join(input_path, "**"),  # Add wildcard for inputted paths
                recursive=Config.ORCHESTRATOR_RECURSIVENESS,
            )

        # For each input folder path, do
        # take only filename, replace to '.' convention for importing, and then take only .py files
        for input_path, files_list in self.files_detected_per_path.items():
            basename_list = [
                f.replace(input_path, "", 1).replace(sep, ".")[1:-3]
                for f in files_list
                if splitext(f)[-1] == ".py"
            ]  # Replace only first instance
            self.files_detected_per_path[input_path] = basename_list

        # Print output
        if not silent:
            # Print out filepaths
            print(
                f"Here are the python files present in the specified paths:\n",
                f"{json.dumps(self.files_detected_per_path, indent=4, sort_keys=True)}",
            )

    def execute(self):
        # TODO: ONLY deals with 1 example script!! -> Should do multiple scripts + multiple input folders to watch as well!
        # TODO: Flat import, flattened to list of all job_modules / pipelines. Should use -> self.pipeline_objects_per_path

        # Import dag modules, explicitly specify only the following
        job_modules = self.import_dag_modules(
            self.files_detected_per_path, ["example_job"]
        )

        # Get all pipeline objects defined in the targetd job script
        pipeline_objects = []
        [
            pipeline_objects.extend(self.get_pipeline_objects(job_module))
            for job_module in job_modules
        ]

        # Test running the pipeline defined in job
        print(f"Full import of all pipeline_objects -> {pipeline_objects}")
        print(
            f"Here is the class attribute for instantiated jobs -> {Pipeline._pipeline_list}"
        )

        # TODO: Print all scheduled tasks for each pipeline
        for pipeline_object in pipeline_objects:
            print(f"{pipeline_object.name} ==> {pipeline_object.task_list}")

        # TODO: Print schedule of execution for pipelines

        # TODO: Give visual representation of connected tasks

        # Run watchdog (For refreshing any time a new file is added)
        watcher = Watcher(Config.WATCHED_FOLDER)
        watcher.run()

        # TODO: Remaining
        """
        - Parse cron string
        - Implement scheduling logic

        - Try extending the example_job script and see if it works with other imports etc.
        """

    @staticmethod
    def get_pipeline_objects(imported_dag_module):
        """
        Returns the instantiated pipeline objects!
        """
        pipeline_objects = []
        public_methods_in_module = [
            method
            for method in imported_dag_module.__dict__.keys()
            if "__" not in method
        ]

        for public_method in public_methods_in_module:
            if not isclass(getattr(imported_dag_module, public_method)) and isinstance(
                getattr(imported_dag_module, public_method), Pipeline
            ):
                pipeline_objects.append(getattr(imported_dag_module, public_method))

        return pipeline_objects

    @staticmethod
    def import_dag_modules(files_dict: dict, only_import_list: list = None):
        """
        Imports all dag modules
        """

        modules_to_return = []

        if not only_import_list:
            for input_path, files_list in files_dict.items():
                for file_path in files_list:
                    modules_to_return.append(import_module(file_path))

        else:
            joined_files_list = sum(files_dict.values(), [])

            for specified_module in only_import_list:
                [
                    modules_to_return.append(import_module(module_name))
                    for module_name in joined_files_list
                    if specified_module in module_name
                ]

        return modules_to_return

    @staticmethod
    def add_to_system_path(paths: list):
        [sys.path.append(p) for p in paths]
