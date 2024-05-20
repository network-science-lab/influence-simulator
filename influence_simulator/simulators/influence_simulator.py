from abc import ABC, abstractmethod
from csv import writer as csv_writer
from typing import NamedTuple
from warnings import warn

from lightning_diffusion.models import DiffusionModel
from networkx import Graph
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


class InfluenceSimulator(ABC):
    def __init__(
        self,
        graph: Graph,
        *,
        random_state: int = None,
    ) -> None:
        self.graph = graph
        self.random_state = random_state
        self.result: list[SimulationResult] = []

    @abstractmethod
    def init_simulation(self, node: int) -> DiffusionModel:
        """
        Initializes the simulation for a given node by creating
        a separate diffusion model and properly setting the initial
        state.

        This step should ensure consistency in concurrent simulations.
        """

    @abstractmethod
    def simulate_node(self, node: int) -> SimulationResult:
        """
        Performs a complete influence simulation for a given node.
        """

    def simulate(
        self,
        *,
        n_jobs: int = 1,
        chunksize: int = 1,
        verbose: bool = True,
    ) -> None:

        if n_jobs == 1:
            if verbose:
                nodes = tqdm(self.graph.nodes)
            else:
                nodes = self.graph.nodes

            self.result = [self.simulate_node(node) for node in nodes]
        else:
            if n_jobs <= 0:
                n_jobs = None

            self.result = process_map(
                self.simulate_node,
                self.graph.nodes,
                chunksize=chunksize,
                max_workers=n_jobs,
                disable=not verbose,
            )

    def save_result(self, path: str) -> None:
        if not self.result:
            warn("Attempting to save empty simulation results.")

        with open(path, "wt", encoding="utf-8") as handle:
            writer = csv_writer(handle)
            writer.writerow(SimulationResult._fields)
            writer.writerows(self.result)
