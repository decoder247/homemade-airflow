from dataclasses import dataclass, field
from datetime import datetime as dt
from typing import Any, Callable, ClassVar, List, Union

from utils import *


@dataclass
class Pipeline:
    name: str
    schedule: str
    task_list: list = field(default_factory=lambda: [])

    _pipeline_list: ClassVar[List] = []

    def __post_init__(self) -> None:
        Pipeline._pipeline_list.append(self.name)

    def print_name(self):
        print(self.name)


@dataclass
class Task:
    task_name: str
    pipeline: Pipeline


@dataclass
class PythonTask(Task):
    python_callable: callable

    def __post_init__(self) -> None:
        self.add_task_to_pipeline()

    def add_task_to_pipeline(self):
        self.pipeline.task_list.append(self.task_name)


@dataclass
class HttpTask:
    pass


@dataclass
class Scheduling:
    # using default_factory -> https://stackoverflow.com/a/69564866
    scheduling: ClassVar[List[Pipeline]] = []
    intermittent_printing: ClassVar[bool] = True

    @classmethod
    def add_pipeline(cls, pl: Pipeline):
        cls.scheduling.append(pl)
