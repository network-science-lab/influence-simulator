import networkx as nx
import pytest

from influence_simulator.utils import load_graph


@pytest.mark.parametrize(
    "graph_format",
    ("gml", "graphml", "pajek", "adjlist", "edgelist"),
)
def test_graph_loading(random_graph: nx.Graph, graph_format: int, tmpdir):
    path = tmpdir.mkdir("graphs").join(f"graph.{graph_format}")

    saving_func = getattr(nx, f"write_{graph_format}")
    saving_func(random_graph, str(path))

    restored = load_graph(str(path))

    # more strict comparison for nodes
    assert sorted(random_graph.nodes) == sorted(restored.nodes)
    assert nx.utils.edges_equal(random_graph.edges, restored.edges)
