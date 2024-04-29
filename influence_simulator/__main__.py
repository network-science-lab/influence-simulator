"""
Script for simulating nodes influence in networks. 
Simulations are run with the Independent Cascade Model
"""

import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from datetime import datetime
from pathlib import Path

import numpy as np

from influence_simulator.influence_simulator import InfluenceSimulator

from .utils import log_memory, timer


rng = np.random.default_rng()


def setup_logging(log_level: str) -> None:
    if log_level.lower() in ("none", "disable"):
        log_level = logging.WARNING + 100
    else:
        log_level = log_level.upper()

    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(message)s",
    )


def get_output_file(
    output_path: str,
    graph_name: str,
    infection_probability: float,
) -> Path:
    path = Path(output_path)

    if not path.suffix:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        salt = rng.integers(0, 1_000)

        path = (
            path
            / graph_name
            / str(infection_probability)
            / f"{graph_name}_{infection_probability}_{timestamp}_{salt}.csv"
        )

        path.parent.mkdir(parents=True, exist_ok=True)

    return path


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("graph", type=str, help="Path to saved graph file")
    parser.add_argument(
        "infection_probability",
        type=float,
        help="Independent Cascade Model parameter.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./simulation_results/",
        help="Output path to store the results. If a folder is given "
        "- whole archive structure will be created in given directory. "
        "(default: ./simulation_results/)",
    )
    parser.add_argument(
        "-r",
        "--random-state",
        type=int,
        default=None,
        help="Seed for random number generation. (default: None)",
    )
    parser.add_argument(
        "-n",
        "--n-jobs",
        type=int,
        default=1,
        help="Number of concurrent workers. (default: 1)",
    )
    parser.add_argument(
        "-c",
        "--chunksize",
        type=int,
        default=1,
        help="Chunksize for concurrent workers. (default: 1)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Display progress bar.",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="info",
        help="Logging level. Provide 'none' to "
        "turn off logging. (default: info)",
    )

    return parser.parse_args()


def main(args: Namespace):
    setup_logging(args.log_level)

    simulator = InfluenceSimulator(
        graph=args.graph,
        infection_probability=args.infection_probability,
        random_state=args.random_state,
    )

    output_file = get_output_file(
        output_path=args.output,
        graph_name=Path(args.graph).stem,
        infection_probability=args.infection_probability,
    )

    simulator.simulate(
        verbose=args.verbose,
        n_jobs=args.n_jobs,
        chunksize=args.chunksize,
    )

    simulator.save_result(output_file)


def cli():
    with timer("Simulation time:", 3):
        main(parse_args())

    log_memory()


if __name__ == "__main__":
    cli()
