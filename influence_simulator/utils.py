import resource
from contextlib import contextmanager
from datetime import timedelta
from logging import getLogger
from time import perf_counter
from typing import Callable

import networkx as nx
from lightning_diffusion.models.diffusion_model import DiffusionModel


logger = getLogger("influence-simulator")


def format_delta(seconds: float, digits: int = -1) -> str:
    """
    Formats time delta with given precision.
    """
    delta = str(timedelta(seconds=seconds))

    if "." in delta:
        if digits == 0:
            delta = delta.split(".", 1)[0]
        elif digits > 0:
            # format microseconds
            delta = delta.split(".")
            delta[1] = delta[1][:digits]
            delta = ".".join(delta)

    return delta


@contextmanager
def timer(message: str = "Time elapsed:", digits: int = -1):
    """
    Context manager based timer.
    """

    start = perf_counter()
    yield
    stop = perf_counter()

    delta = format_delta(seconds=(stop - start), digits=digits)

    logger.info(f"{message} {delta}")


def log_memory():
    memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

    logger.info(f"Memory used: {memory:_.2f} MiB")


def get_loading_function(path: str) -> Callable:
    extension = path.split(".")[-1]
    try:
        func = getattr(nx, f"read_{extension}")
    except AttributeError as exc:
        raise ValueError(f"Graph format '{extension}' not supported.") from exc

    return func


def relabel_nodes(graph: nx.Graph) -> nx.Graph:
    """
    Changes type of node labels to ints.
    '0' -> 0
    """
    mapping = {}
    for i in range(len(graph)):
        mapping[str(i)] = i

    return nx.relabel_nodes(graph, mapping)


def load_graph(path: str) -> nx.Graph:
    loading_function = get_loading_function(path)
    graph = loading_function(path)

    if isinstance(graph, nx.MultiGraph):
        graph = nx.Graph(graph)

    graph = relabel_nodes(graph)
    DiffusionModel.validate_graph(graph)

    return graph
