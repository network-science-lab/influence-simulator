from csv import writer as csv_writer
from typing import Callable, NamedTuple

import networkx as nx
from lightning_diffusion.models import IndependentCascadeModel
from tqdm.auto import tqdm
from tqdm.contrib.concurrent import process_map


class Peak(NamedTuple):
    infected: int
    iteration: int


class SimulationResult(NamedTuple):
    node: int
    simulation_length: int
    exposed: int
    not_exposed: int
    peak_infected: int
    peak_iteration: int


class InfluenceSimulator:
    def __init__(
        self,
        graph: nx.Graph | str,
        infection_probability: float,
        *,
        random_state: int = None,
    ) -> None:
        if isinstance(graph, nx.Graph):
            self.graph = graph
        else:
            self.graph = self.load_graph(graph)

        self.infection_probability = infection_probability
        self.random_state = random_state

        self.result: list[SimulationResult] = []

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

        peak = Peak(0, 0)
        while not model.terminated:
            model.step()

            if (infected := model.state_summary["infected"]) > peak.infected:
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

    def simulate(self, *, n_jobs: int = 1, verbose: bool = True) -> None:
        if n_jobs <= 0:
            n_jobs = None

        if n_jobs == 1:
            if verbose:
                nodes = tqdm(self.graph.nodes)
            else:
                nodes = self.graph.nodes

            self.result = [self.simulate_node(node) for node in nodes]
        else:
            nodes = self.graph.nodes
            self.result = process_map(
                self.simulate_node, nodes, disable=not verbose
            )

    @staticmethod
    def get_loading_function(path: str) -> Callable:
        extension = path.split(".")[-1]
        try:
            func = getattr(nx, f"read_{extension}")
        except AttributeError as e:
            raise ValueError(
                f"Graph format '{extension}' not supported."
            ) from e

        return func

    @staticmethod
    def load_graph(path: str) -> nx.Graph:
        loading_function = InfluenceSimulator.get_loading_function(path)
        graph = loading_function(path)
        graph = nx.convert_node_labels_to_integers(graph)
        return graph

    def save_result(self, path: str) -> None:
        with open(path, "wt", encoding="utf-8") as handle:
            writer = csv_writer(handle)
            writer.writerow(SimulationResult._fields)
            writer.writerows(self.result)
