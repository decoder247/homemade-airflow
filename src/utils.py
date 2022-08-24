from datetime import datetime as dt
from glob import glob
from os import getcwd, remove
from os.path import basename, exists, join
from sched import scheduler
from sys import path
from time import sleep, time
from typing import Any, Union

from croniter import croniter
from networkx import DiGraph, all_neighbors
from networkx.drawing.nx_pydot import to_pydot
from pydot import Dot
from pytz import timezone as tz

# def check_if_substring_in_list(substring: str, input_list: list):
#     return any([True for string in input_list if substring in string])


def add_to_system_path(paths: list) -> None:
    [path.append(p) for p in paths]


def get_files_in_folder(input_path_string: str, recursive: bool = False):
    if recursive and input_path_string[-2:] != "**":
        raise ValueError(
            f"Expected '**' at end of input_path_string - {input_path_string}"
        )
    return glob(input_path_string, recursive=recursive)


def create_croniter(cron_str: str, base: dt = dt.now(tz("UTC")), silent: bool = True):
    if croniter.is_valid(cron_str):
        c = croniter(cron_str, base)
        if not silent:
            print(f"Croniter object created! Timezone set to - {c.tzinfo}")
        return c
    else:
        raise ValueError(f"Invalid input string - {cron_str}")


def croniter_get_sequence(
    cron: croniter, sequence: str = "next", return_type: Union[dt, float] = dt
):
    ALLOWABLE_RETURN_TYPES = [dt, float]
    ALLOWABLE_SEQUENCE_VALUES = ["current", "next", "prev"]
    assert (
        return_type in ALLOWABLE_RETURN_TYPES
    ), f"Return type not in list of allowable inputs - {ALLOWABLE_RETURN_TYPES}"
    assert (
        sequence in ALLOWABLE_SEQUENCE_VALUES
    ), f"Specified sequence not in list of allowable inputs - {ALLOWABLE_SEQUENCE_VALUES}"

    if sequence == "current":
        return cron.get_current(ret_type=return_type)
    elif sequence == "prev":
        return cron.get_prev(ret_type=return_type)
    elif sequence == "next":
        return cron.get_next(ret_type=return_type)
    else:
        raise ValueError("Unknown error in croniter_get_sequence")


def create_digraph(nodes: list = None, edges: list = None) -> DiGraph:
    g = DiGraph()
    if not nodes and not edges:
        pass
    else:
        if edges:
            g.add_edges_from(edges)
        elif nodes:
            g.add_nodes_from(nodes)
    return g


def check_nodes_are_connected(input_graph: DiGraph, node1, node2):
    flatten_list = lambda x: list(sum(x, ()))

    all_nodes_connected_to_node2 = flatten_list(
        list(input_graph.out_edges(node2)) + list(input_graph.in_edges(node2))
    )
    connected_nodes = list(set(all_nodes_connected_to_node2))
    connected_nodes.remove(node2)

    return node1 in connected_nodes


def show_graph(
    dot_object: Dot,
    save: bool = False,
    view: bool = True,
    graph_title: str = "network_graph",
    filename: str = None,
    format: str = "png",
) -> None:
    from graphviz import Source

    ALLOWED_GRAPH_SAVE_FORMATS = ["png", "pdf"]
    if not filename:
        filename = join(getcwd(), f"{graph_title}")

    assert (
        format in ALLOWED_GRAPH_SAVE_FORMATS
    ), f"Format not in allowable list -> {ALLOWED_GRAPH_SAVE_FORMATS}"
    assert not exists(filename) and not exists(
        f"{filename}.{format}"
    ), f"Path already exists! Can't save to -> {filename}"

    dot_string = get_graph_pydot_string(dot_object)
    gv_src = Source(dot_string, filename=filename, format=format)
    if view:
        gv_src.view()
        if not save:
            sleep(1)
    if not save:
        if exists(f"{filename}"):
            remove(f"{filename}")
        else:
            print(f"WARNING: '{filename}' does not exist!")
        if exists(f"{filename}.{format}"):
            remove(f"{filename}.{format}")
        else:
            print(f"WARNING: '{filename}.{format}' does not exist!")

    return None


def get_all_neighbours(graph: DiGraph, node: str):
    return all_neighbors(graph=graph, node=node)


def get_graph_pydot_string(dot_input: Dot):
    return dot_input.to_string()


def get_graph_pydot(input_graph: DiGraph):
    return to_pydot(input_graph)


def create_scheduler():
    return scheduler(time, sleep)


def enter_schedule(
    schedule_obj: scheduler, delay, priority, action, argument=(), kwargs={}
) -> None:
    """
    https://docs.python.org/3/library/sched.html#sched.scheduler.enter
    """
    schedule_obj.enter(delay, priority, action, argument=(), kwargs={})
    return None
