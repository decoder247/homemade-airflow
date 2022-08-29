import json
from datetime import datetime as dt
from importlib import import_module
from inspect import isclass
from os import cpu_count, sep
from os.path import dirname, exists, isfile, join, splitext
from time import sleep

from celery import Celery, chain, signature
from pytz import timezone as tz
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from celeryconfig import CeleryConfig
from config import Config as C
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

        for watched_extension in C.WATCHED_FILE_EXTENSIONS:
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
                sleep(5)
        except Exception as e:
            self.observer.stop()
            print(f"Watchdog Error!! - {e}")

        self.observer.join()


class Worker:
    """
    Attributes:
    - Pending tasks
    - Finished tasks

    - Executes in a thread
    """

    pending_tasks = []
    finished_tasks = []

    def __init__(self) -> None:
        self.cpu_count = cpu_count()


class Orchestrator:
    """
    Main orchestrator method

    TODO: Allow more input paths, i.e. schedule "/asd/folder1" "/asd/folder2"
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
        self.scheduling = Scheduling()
        self.celery = Celery(main="tasks", config_source=CeleryConfig)

        # first Remove any trailing '/' if present
        workflow_input_paths = [dirname(join(p, "")) for p in workflow_input_paths]

        # Add to system path so it's findable
        add_to_system_path(workflow_input_paths)

        # Check if folder exists for each path
        for input_path in workflow_input_paths:
            self.files_detected_per_path[input_path] = get_files_in_folder(
                join(input_path, "**"),  # Add wildcard for inputted paths
                recursive=C.ORCHESTRATOR_RECURSIVENESS,
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

        if not silent:
            print(
                f"Python files present in {input_path}:\n",
                f"{json.dumps(self.files_detected_per_path, indent=4, sort_keys=True)}",
            )

    def execute(self):
        _ = self.import_dag_modules(
            self.files_detected_per_path, only_import_list=["example_job"]
        )

        # Print pipelines in schedule
        print(f"Pipeline queue \t\t\t=> {self.scheduling.pipeline_queue}")
        print(
            f"Pipelines defined and imported \t=> "
            f"{[p.pipeline_id for p in self.scheduling.pipeline_list]}"
        )
        for p in self.scheduling.pipeline_list:
            print(f"Tasks in '{p.pipeline_id}' \t=> {p.task_list}")

        # Create the task flows (DAGs) per defined pipeline
        view_flag = not is_docker()  # Dynamically don't view dag
        if is_docker():
            print(f"Running on docker container!!")
        for p in self.scheduling.pipeline_list:
            p.create_dag(silent=False)
            p.show_dag(silent=False, view=view_flag)
            p.refresh_task_queue()
            print(
                f"Order of task sequence for '{p.pipeline_id}' -> ",
                p.task_queue_str,
            )

        # Get the base queue -> queue of times for each pipeline
        # Then, build / resolve the main queue -> queue times of earliest pipeline
        # NOTE: resolving queue will remove things from base queue!!
        self.scheduling.resolve_queue(silent=False)
        # When being resolved -> if pipeline is finished, state should be updated...

        # Print for debugging purposes
        for key, dt_list in self.scheduling.pipeline_base_queue.items():
            print(
                f"\n{len(dt_list)} execution orders queued in {self.scheduling._get_pipeline_id_from_uuid(key)}___{str(key)} -> {[el.strftime('%Y%d%m %H:%M:%S') for el in dt_list]}\n"
            )
        printable_list = []
        for el in self.scheduling.pipeline_queue:
            uuid, execute_dt = list(el.items())[0]
            printable_list.append(
                {
                    self.scheduling._get_pipeline_id_from_uuid(
                        uuid
                    ): execute_dt.strftime("%y%m%d-%H:%M:%S")
                }
            )
        print(f"Earliest pipelines to execute - {printable_list}")

        # TODO: Execute tasks in pipeline via celery (Consider using beat for continually periodic tasks?)
        for pipeline_ref in self.scheduling.pipeline_queue:
            assert (
                len(pipeline_ref.items()) == 1
            ), "Length of pipeline_ref dictionary is more than 1!"
            uuid, dt_obj = list(pipeline_ref.items())[0]
            pl_to_execute = self.scheduling._get_pipeline_object_from_uuid(uuid)

            if pl_to_execute.task_queue:
                self.execute_pipeline_with_celery(pl_to_execute, dt_obj)
            else:
                print(
                    f"Pipeline '{pl_to_execute.pipeline_id}' has no tasks queued! Skipping execution..."
                )

        # Run watchdog (For refreshing any time a new file is added in the monitored dag folder)
        watcher = Watcher(C.WATCHED_FOLDER)
        watcher.run()

    def execute_celery(self):
        self.refresh_celery_tasks()

        # Send example task
        r = self.celery.send_task("tasks.addTask", args=[2, 2], kwargs={})

        # Execute celery task which executes a function name + it's source
        r = self.celery.send_task(
            "tasks.executeDAGTask",
            args=[
                "/dags",
                "example_job",
                "print_something",
                ["hello_this_is_something!!"],
            ],
            kwargs={},
        )

    def execute_pipeline_with_celery(self, pipeline: Pipeline, input_dt: dt) -> None:
        # NOTE: Can only execute flat lists for now
        flattened_task_list = []
        for task in pipeline.task_queue:
            flattened_task_list.extend(task)

        # Execute celery
        cel_signature_list = []
        for task in flattened_task_list:
            args = [
                "/dags",
                self._get_module_import_str(task.python_callable_path, "/dags"),
                task.python_callable_func_name,
            ]
            if task.op_args:
                args.append(task.op_args)

            s = signature(
                "tasks.executeDAGTask",
                args=args,
                kwargs={},
                immutable=True,  # NOTE: So that when chaining, previous task doesn't pass the result to the next task as args!!
            )
            cel_signature_list.append(s)

        # Execute in chain
        print(
            f"Executing {pipeline.pipeline_id} ({len(cel_signature_list)} tasks) at -> "
            f"{input_dt.astimezone(tz('Europe/Amsterdam'))}"
        )
        res = chain(cel_signature_list).delay(eta=input_dt)
        # print(res.status, res.get(timeout=10))
        # if res.status == "SUCESS":
        #     print(res.get())
        # sleep(20)

    def refresh_celery_tasks(self) -> None:
        self.celery.autodiscover_tasks()

    def _OLD_create_celery_task(self) -> None:
        """
        Task to create a celery task programatically. Not working for now

        Leads:
        * https://stackoverflow.com/a/69431092/10002593
        """
        # Register tasks
        ct = self.celery._task_from_fun(Orchestrator._subtract, name="subtractTask")
        self.celery.tasks.register(ct)
        self.refresh_celery_tasks()
        sleep(0.5)
        print("BEFORE registered tasks ->", self.celery.control.inspect().registered())
        self.celery.control.shutdown(destination=["celery@worker-1"])  # Restart worker
        sleep(4)
        self.refresh_celery_tasks()
        sleep(2)
        print("AFTER registered tasks ->", self.celery.control.inspect().registered())

        self.celery.conf.CELERY_IMPORTS = ("tasks",)

    def _OLD(self, imported_job_modules: list):
        # Get all pipeline objects defined in the targetd job script
        pipeline_objects = []
        [
            pipeline_objects.extend(self.get_pipeline_objects(job_module))
            for job_module in imported_job_modules
        ]

    @staticmethod
    def _get_module_import_str(input_path: str, root_folder: str = None) -> str:
        if root_folder:
            input_path = input_path.replace(root_folder, "", 1).lstrip(sep)

        return splitext(input_path)[0].replace(sep, ".")

    @staticmethod
    def _subtract(x: int, y: int) -> int:
        return x + y

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
