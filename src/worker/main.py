from importlib import import_module
from os import getcwd
from os.path import exists, join
from sys import path
from typing import Callable

from celery import Celery

from celeryconfig import CeleryConfig
from config import Config as C
from utils import *

app = Celery(main="tasks", config_source=CeleryConfig)


@app.task(name="tasks.addTask")  # can just be 'addTask'
def add(x: int, y: int) -> int:
    return x + y


@app.task(name="tasks.executeDAGTask")
def execute_dag_task(
    dag_root_folder: str,
    dag_module_str: str,
    func_name: str,
    func_args: list = None,
    func_kwargs: dict = None,
) -> None:
    """
    https://stackoverflow.com/a/37724523

    Executes a task (i.e. function) as defined in a folder

    inside.example_job_2
    """

    # Add to system path if not present
    if dag_root_folder not in path:
        path.append(dag_root_folder)
        path.append(C.DOCKER_SOURCE_CODE_PATH)

    # Import module after it has been appended
    dag_module = import_module(dag_module_str)

    # Execute function
    func = getattr(dag_module, func_name)

    if func_args and func_kwargs:
        func(*func_args, **func_kwargs)
    elif func_args:
        func(*func_args)
    elif func_kwargs:
        func(**func_kwargs)
    else:
        func()
