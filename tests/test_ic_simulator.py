import pytest
from networkx import Graph

from influence_simulator.simulators import IndependentCascadeSimulator


@pytest.mark.parametrize("node", range(5))
def test_init(random_graph: Graph, node: int):
    sim = IndependentCascadeSimulator(random_graph, 0.1)
    model = sim.init_simulation(node)

    assert model.state[node] == "infected"
    assert model.state_summary["susceptible"] == len(random_graph) - 1


def test_simulation(random_graph: Graph):
    sim = IndependentCascadeSimulator(random_graph, 0.2)
    sim.simulate(verbose=False)
    assert len(sim.result) > 0

    sim = IndependentCascadeSimulator(random_graph, 0.0)
    sim.simulate(verbose=False)

    for row in sim.result:
        assert row.simulation_length == 1
        assert row.exposed == 1
        assert row.peak_infected == 1
        assert row.peak_iteration == 0


@pytest.mark.parametrize("random_state", range(5))
def test_concurrent(random_state: int, random_graph: Graph):
    sim = IndependentCascadeSimulator(
        random_graph, 0.2, random_state=random_state
    )
    sim.simulate(n_jobs=1, verbose=False)
    result_single = sim.result

    sim = IndependentCascadeSimulator(
        random_graph, 0.2, random_state=random_state
    )
    sim.simulate(n_jobs=4, verbose=False)
    result_multi = sim.result

    assert result_single == result_multi
