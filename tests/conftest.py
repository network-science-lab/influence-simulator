from networkx import Graph, barabasi_albert_graph
from pytest import fixture


@fixture(scope="function")
def random_graph() -> Graph:
    return barabasi_albert_graph(100, 3)
