from lightning_diffusion.models import IndependentCascadeModel
from networkx import Graph

from .influence_simulator import InfluenceSimulator, Peak, SimulationResult


class IndependentCascadeSimulator(InfluenceSimulator):
    def __init__(
        self,
        graph: Graph,
        infection_probability: float,
        *,
        random_state: int = None,
    ) -> None:
        self.infection_probability = infection_probability

        super().__init__(graph=graph, random_state=random_state)

    def init_simulation(self, node: int) -> IndependentCascadeModel:
        model = IndependentCascadeModel(
            graph=self.graph,
            initially_infected=0,
            infection_probability=self.infection_probability,
            random_state=self.random_state,
        )
        model.state[node] = "infected"

        return model

    def simulate_node(self, node: int) -> SimulationResult:
        model = self.init_simulation(node)

        peak = Peak(infected=1, iteration=0)
        while not model.terminated:
            model.step()

            if (infected := model.state.count("infected")) > peak.infected:
                peak = Peak(infected, model.iteration)

        final_state = model.state_summary
        return SimulationResult(
            node=node,
            simulation_length=model.iteration,
            exposed=final_state["recovered"],
            not_exposed=final_state["susceptible"],
            peak_infected=peak.infected,
            peak_iteration=peak.iteration,
        )
