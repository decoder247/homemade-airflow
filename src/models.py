from dataclasses import dataclass, field
from datetime import datetime as dt
from enum import Enum
from typing import Any, Callable, ClassVar, List, Tuple, Union

import networkx as nx
from networkx import DiGraph
from sklearn import pipeline

from utils import *


class TaskState(Enum):
    ERRORED = -1
    STOPPED = 0
    SUCCESSFUL = 1
    QUEUED = 2
    RUNNING = 3


@dataclass
class Scheduling:
    queue: ClassVar[List] = []
    pipeline_list: ClassVar[List] = []

    intermittent_printing: ClassVar[bool] = True

    def resolve_queue(self, max_num_items: int = None):
        # TODO
        pass


@dataclass
class TaskBase:
    task_id: str


@dataclass
class DAGTasksInfo:
    nodes: list = field(init=False, default_factory=lambda: [])
    edges: List[Tuple[TaskBase, ...]] = field(init=False, default_factory=lambda: [])


@dataclass
class DAG(DAGTasksInfo):
    # init false so it's optional, and also prevents error when task is inherited, and further attributes are defined
    graph: DiGraph = field(init=False, default_factory=lambda: DiGraph())

    def __post_init__(self):
        if self.nodes:
            self.create_dag()

    def create_dag(self):
        self.graph = create_digraph(self.nodes, self.edges)

    def get_order(self, flat: bool = True):
        if flat:
            return nx.topological_sort(self.graph)
        else:
            # copy the graph
            _g = self.graph.copy()
            res = []
            # while _g is not empty
            while _g:
                zero_indegree = [v for v, d in _g.in_degree() if d == 0]
                res.append(zero_indegree)
                _g.remove_nodes_from(zero_indegree)
            return res


@dataclass
class Pipeline(DAG):
    name: str
    schedule: str
    task_list: list = field(default_factory=lambda: [])

    _pipeline_list: ClassVar[List] = []

    def __post_init__(self) -> None:
        self.schedule = create_croniter(self.schedule)  # Ugly way of converting type!

        Scheduling.pipeline_list.append(self)
        Pipeline._pipeline_list.append(self.name)

    def show_dag(self, silent: bool = False):
        if len(self.task_list) <= 0:
            if not silent:
                print(
                    f"WARNING: No tasks in pipeline '{self.name}', not displaying graph..."
                )
        else:
            if not silent:
                print(f"Displaying graph for pipeline - '{self.name}")
            show_graph(get_graph_pydot(self.graph), save=False, view=True)

    def print_name(self):
        print(self.name)


@dataclass
class Task(TaskBase):
    pipeline: Pipeline
    order: int = field(init=False, default=None)
    state: TaskState = field(init=False, default=TaskState.STOPPED)


@dataclass
class PythonTask(Task):
    python_callable: callable

    def __post_init__(self) -> None:
        self.add_task_to_pipeline()
        self.add_task_to_DAGTasksInfo()

    def add_task_to_pipeline(self):
        self.pipeline.task_list.append(self.task_id)

    def add_task_to_DAGTasksInfo(self):
        self.pipeline.nodes.append(self.task_id)

    def set_upstream(self, task: Task):
        self.pipeline.edges.append((task.task_id, self.task_id))

    def set_downstream(self, task: Task):
        self.pipeline.edges.append((self.task_id, task.task_id))


@dataclass
class HttpTask(Task):
    pass
