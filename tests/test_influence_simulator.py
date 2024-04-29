import networkx as nx
import pytest

from influence_simulator import InfluenceSimulator


def random_graph() -> nx.Graph:
    return nx.barabasi_albert_graph(100, 3)


@pytest.mark.parametrize("node", range(5))
def test_init(node: int):
    graph = random_graph()
    sim = InfluenceSimulator(graph, 0.1)
    model = sim.init_simulation(node)

    assert model.state[node] == "infected"
    assert model.state_summary["susceptible"] == len(graph) - 1


@pytest.mark.parametrize(
    "graph_format",
    ("gml", "graphml", "pajek", "adjlist", "edgelist"),
)
def test_graph_loading(graph_format: int, tmpdir):
    graph = random_graph()
    path = tmpdir.mkdir("graphs").join(f"graph.{graph_format}")

    saving_func = getattr(nx, f"write_{graph_format}")
    saving_func(graph, str(path))

    restored = InfluenceSimulator.load_graph(str(path))

    # more strict comparison for nodes
    assert sorted(graph.nodes) == sorted(restored.nodes)
    assert nx.utils.edges_equal(graph.edges, restored.edges)
