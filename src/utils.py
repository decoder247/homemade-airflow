from datetime import datetime as dt
from datetime import timezone as tz
from glob import glob
from os import getcwd, remove
from sched import scheduler
from time import sleep, time
from os.path import join, exists, basename

import networkx as nx
from croniter import croniter
from graphviz import Source
from networkx import DiGraph
from networkx.drawing.nx_pydot import to_pydot
from pydot import Dot

# def check_if_substring_in_list(substring: str, input_list: list):
#     return any([True for string in input_list if substring in string])


def get_files_in_folder(input_path_string: str, recursive: bool = False):
    if recursive and input_path_string[-2:] != "**":
        raise ValueError(
            f"Expected '**' at end of input_path_string - {input_path_string}"
        )
    return glob(input_path_string, recursive=recursive)


def create_croniter(cron_str: str, base: dt = dt.now(tz.utc), silent: bool = True):
    if croniter.is_valid(cron_str):
        c = croniter(cron_str, base)
        if not silent:
            print(f"Croniter object created! Timezone set to - {c.tzinfo}")
        return c
    else:
        raise ValueError(f"Invalid input string - {cron_str}")


def create_digraph(nodes: list = None, edges: list = None) -> DiGraph:
    if not nodes and not edges:
        return DiGraph()
    else:
        g = DiGraph()
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
    filename: str = None,
    format: str = "png",
) -> None:
    ALLOWED_GRAPH_SAVE_FORMATS = ["png", "pdf"]
    if not filename:
        filename = join(getcwd(), f"network_graph")

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
        remove(f"{filename}")
        remove(f"{filename}.{format}")

    return None


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
