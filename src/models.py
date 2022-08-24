import inspect
from dataclasses import dataclass, field
from datetime import datetime as dt
from enum import Enum
from os import stat
from os.path import abspath
from typing import Any, Callable, ClassVar, Dict, List, Tuple, Union
from uuid import UUID, uuid4

import networkx as nx
from networkx import DiGraph

from config import Config as C
from utils import *


@dataclass
class TaskState(Enum):
    QUEUED = 2
    ERRORED = -1
    STOPPED = 1
    SUCCESSFUL = 0
    RUNNING = 3


@dataclass
class PipelineState(Enum):
    ERRORED = -1
    STOPPED = 1
    COMPLETED = 0
    RUNNING = 2


@dataclass
class TaskBase:
    task_uuid: UUID = field(init=False, default_factory=lambda: uuid4())
    task_id: str


@dataclass
class DAGTasksInfo:
    nodes: list = field(init=False, default_factory=lambda: [])
    edges: List[Tuple[TaskBase, ...]] = field(init=False, default_factory=lambda: [])


@dataclass
class PipelineBase:
    pipeline_uuid: UUID = field(init=False, default_factory=lambda: uuid4())
    pipeline_id: str


@dataclass
class Scheduling:
    """
    TODO:
    -> Create a safe execute / consume_pipeline method that pops from pipeline_queue, updates states etc.
    """

    pipeline_queue: ClassVar[List[Dict[UUID, dt]]] = []
    pipeline_base_queue: ClassVar[Dict[UUID, List[dt]]] = {}
    pipeline_list: ClassVar[List[PipelineBase]] = []

    max_num_in_queue: int = field(default=C.PIPELINE_QUEUE_MAX_LENGTH)
    max_num_in_base_queue: int = field(default=C.PIPELINE_BASE_QUEUE_MAX_LENGTH)
    intermittent_printing: ClassVar[bool] = True

    def resolve_queue(self, silent: bool = True):
        """
        pipeline_queue = [
            {'pipeline_uuid_1': [22-08-16 09:10, 0]},
            {'pipeline_uuid_1': [22-08-16 09:15, 2]},        --> If 2 times are the same, should execute based on priority! Otherwise
            {'pipeline_uuid_2': [22-08-16 09:15, 0]}
        ]
        """
        if not self._pipeline_is_not_empty() and not silent:
            print(f"Cannot resolve queue. Pipeline list in scheduler is empty!")
            return

        print(
            f"\nResolving / refreshing queue... Currently {len(self.pipeline_queue)}/{self.max_num_in_queue} "
            f"pipeline items in queue already."
        )

        while len(self.pipeline_queue) < self.max_num_in_queue:
            """
            Compares the first execution time for each pipeline in the base queue. Takes the earliest (i.e. 'lowest datetime') value to
            execute.

            WRAP THIS into function, i.e. function of popping base queue and adding to main queue
            """
            pipeline_uuid_keys = sorted(self.pipeline_base_queue.keys())
            earliest_pline_and_execute_time_so_far = {
                pipeline_uuid_keys[0]: self.pipeline_base_queue[pipeline_uuid_keys[0]][
                    0
                ]  # NOTE: WILL ERROR out if empty!
            }

            for pipeline_uuid in pipeline_uuid_keys[1:]:
                first_execution_time = self.pipeline_base_queue[pipeline_uuid][
                    0
                ]  # NOTE: WILL ERROR out if empty!
                earliest_execute_time_so_far = list(
                    earliest_pline_and_execute_time_so_far.values()
                )[0]
                if first_execution_time < earliest_execute_time_so_far:
                    earliest_pline_and_execute_time_so_far = {
                        pipeline_uuid: first_execution_time
                    }

            # Add execution time to main queue
            # NOTE: SORT out priority value
            self.pipeline_queue.append(earliest_pline_and_execute_time_so_far)

            # Remove execution time from the base queue
            # NOTE: Might need to rerun refresh base queue after popping!!
            earliest_pipeline_uuid, earliest_execute_time = (
                list(earliest_pline_and_execute_time_so_far.keys())[0],
                list(earliest_pline_and_execute_time_so_far.values())[0],
            )
            self.pipeline_base_queue[earliest_pipeline_uuid].remove(
                earliest_execute_time
            )

    def refresh_base_queue(self):
        """
        pipeline_base_queue = {
                'pipeline_1_uuid': [09.00, 10.00, ...],
                'pipeline_2_uuid': [09.20, 09.40, ...]
            }
        """
        for pipeline_uuid, execution_time_queue in self.pipeline_base_queue.items():
            while len(execution_time_queue) < self.max_num_in_base_queue:
                pipeline_object = self._get_pipeline_object_from_uuid(pipeline_uuid)
                self.pipeline_base_queue[pipeline_uuid] += [
                    croniter_get_sequence(pipeline_object.schedule, "next")
                ]

    def _check_last_refresh_time():
        # TODO:
        # Assign an attribute for last refresh time -> and check if queue length is 20, and if not, check last refresh time (< 5 minutes)
        # This refresh time is useful because

        # Also check if base queue should be refreshed, i.e. based on end_time
        pass

    def _get_pipeline_id_from_uuid(self, uuid: UUID) -> str:
        return self._get_pipeline_object_from_uuid(uuid).pipeline_id

    def _get_pipeline_object_from_uuid(self, uuid: UUID) -> PipelineBase:
        pipeline_object = [
            p for p in self.pipeline_list if p.pipeline_uuid.__eq__(uuid)
        ]
        if len(pipeline_object) != 1:
            print(
                [p.pipeline_id for p in self.pipeline_list],
                [p.pipeline_uuid for p in pipeline_object],
            )
            print(
                f"Length of returned pipeline object from a UUID search of pipeline_result returns more than 1 pipeline!"
            )
            raise ValueError
        return pipeline_object[0]

    def _get_pipeline_ids(self) -> list:
        return [p.pipeline_id for p in self.pipeline_list]

    def _pipeline_is_not_empty(self) -> bool:
        return len(self.pipeline_list) > 0


@dataclass
class DAG(DAGTasksInfo):
    # init false so it's optional, and also prevents error when task is inherited, and further attributes are defined
    graph: DiGraph = field(init=False, default_factory=lambda: DiGraph())

    def __post_init__(self):
        if self.nodes:
            self.create_dag()

    # NOTE:
    # NOT CORRECT --> check!
    # res = nx.topological_generations(self.graph)
    def _get_order(self, flat: bool = True, short_form: bool = False):
        if flat:
            if short_form:
                return [
                    f"{t.task_id}___{t.task_uuid}"
                    for t in list(nx.topological_sort(self.graph))
                ]
            else:
                return nx.topological_sort(self.graph)
        else:
            # copy the graph
            _g = self.graph.copy()
            res = []
            # while _g is not empty
            while _g:
                zero_indegree = [v for v, d in _g.in_degree() if d == 0]
                if short_form:
                    res.append([t.task_id for t in zero_indegree])
                else:
                    res.append(zero_indegree)
                _g.remove_nodes_from(zero_indegree)

            return res


@dataclass
class Pipeline(DAG, PipelineBase):
    pipeline_state: PipelineState = field(init=False, default=PipelineState.STOPPED)
    num_runs_completed: int = field(init=False, default=0)
    schedule: str
    task_list: List[TaskBase] = field(default_factory=lambda: [])
    task_queue: List[List[TaskBase]] = field(init=False, default_factory=lambda: [])
    task_queue_str: List[str] = field(init=False, default_factory=lambda: [])

    def __post_init__(self) -> None:
        self.schedule = create_croniter(self.schedule)  # Ugly way of converting type!

        self._append_pipeline_and_instantiate_base_queue()

    def create_dag(self, silent: bool = True):
        if self._task_exists():
            self.graph = create_digraph(self.nodes, self.edges)
            if not silent:
                print(f"Graph created for pipeline '{self.pipeline_id}'.")
        else:
            if not silent:
                print(
                    f"WARNING: No tasks in pipeline '{self.pipeline_id}'. Graph NOT created..."
                )

    def show_dag(self, silent: bool = True, save: bool = False, view: bool = False):
        if self._task_exists():
            if not silent:
                print(f"Displaying graph for pipeline - '{self.pipeline_id}")
            show_graph(
                get_graph_pydot(self.graph),
                view=view,
                save=save,
                graph_title=self.pipeline_id,
            )
        else:
            if not silent:
                print(
                    f"WARNING: No tasks in pipeline '{self.pipeline_id}', not displaying graph..."
                )

    def refresh_task_queue(self):
        self.task_queue = self._get_order(flat=False, short_form=False)
        self.task_queue_str = self._get_order(flat=False, short_form=True)

    def print_name(self):
        print(self.pipeline_id)

    def _append_pipeline_and_instantiate_base_queue(self) -> None:
        Scheduling.pipeline_list.append(self)

        if self.pipeline_uuid not in Scheduling.pipeline_base_queue.keys():
            Scheduling.pipeline_base_queue[self.pipeline_uuid] = []

    def _task_exists(self):
        return len(self.task_list) > 0


@dataclass
class Task(TaskBase):
    pipeline: Pipeline
    order_number: int = field(init=False, default=None)
    task_state: TaskState = field(init=False, default=TaskState.STOPPED)


@dataclass
class PythonTask(Task):
    python_callable: callable
    python_callable_path: str = field(init=False, default=None)
    python_callable_func_name: str = field(init=False, default=None)
    DEBUG_MODE: bool = False
    op_args: list = field(default=None)

    def __post_init__(self) -> None:
        self._add_task_to_pipeline()
        self._add_task_to_DAGTasksInfo()

        if self.python_callable_path == None:
            self.python_callable_path = abspath(inspect.getfile(self.python_callable))
        if self.python_callable_func_name == None:
            self.python_callable_func_name = self.python_callable.__name__

    def set_upstream(self, task: Task):
        if self.DEBUG_MODE:
            self.pipeline.edges.append((str(task), str(self)))
        else:
            self.pipeline.edges.append((task, self))

    def set_downstream(self, task: Task):
        if self.DEBUG_MODE:
            self.pipeline.edges.append((str(self), str(task)))
        else:
            self.pipeline.edges.append((self, task))

    def get_upstream(self, graph: DiGraph, list_return: bool = True):
        if list_return:
            return list(graph.predecessors(self))
        else:
            return graph.predecessors(self)

    def get_downstream(self, graph: DiGraph, list_return: bool = True):
        if list_return:
            return list(graph.successors(self))
        else:
            return graph.successors(self)

    def _add_task_to_pipeline(self):
        self.pipeline.task_list.append(self.task_id)

    def _add_task_to_DAGTasksInfo(self):
        if self.DEBUG_MODE:
            self.pipeline.nodes.append(str(self))
        else:
            self.pipeline.nodes.append(self)

    def __str__(self):
        return f"{self.task_id}___{self.task_uuid}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.task_id == other.task_id


@dataclass
class HttpTask(Task):
    pass
