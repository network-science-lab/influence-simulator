"""
Script for simulating nodes influence in networks. 
"""

import json
import logging
import shutil
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from . import simulators
from .utils import load_graph, log_memory, timer


def setup_logging(log_level: str) -> None:
    if log_level.lower() in ("none", "disable"):
        log_level = logging.WARNING + 100
    else:
        log_level = log_level.upper()

    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(message)s",
    )


def save_archive(
    model: simulators.InfluenceSimulator,
    output_dir: Path,
    graph_file: str,
    model_config_path: str,
) -> None:

    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    graph_name = Path(graph_file).stem
    output_file = f"{graph_name}_{timestamp}"

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        model.save_result(temp_dir / "simulation_results.csv")
        shutil.copy(model_config_path, temp_dir / "model_config.json")
        shutil.make_archive(output_dir / output_file, "zip", temp_dir)


def load_simulator(
    model_config_path: str,
    graph_path: str,
) -> simulators.InfluenceSimulator:
    with open(model_config_path, encoding="utf-8") as handle:
        config = json.load(handle)

    graph = load_graph(graph_path)
    model_type = getattr(simulators, config.pop("type"))

    return model_type(graph=graph, **config)


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument("graph", type=str, help="Path to saved graph file")
    parser.add_argument(
        "model_config",
        type=str,
        help="Path to a json file containing the configuration for "
        "the simulation model. File should contain 'type' key with the name "
        "of the model class and all required keyword arguments.",
    )

    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        default="./simulation_results/",
        help="Output path to store the results. If a folder is given "
        "- script will create an archive with the results and model config. "
        "(default: ./simulation_results/)",
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

    simulator = load_simulator(args.model_config, args.graph)

    simulator.simulate(
        verbose=args.verbose,
        n_jobs=args.n_jobs,
        chunksize=args.chunksize,
    )

    output_path = Path(args.output_path)
    if output_path.suffix:
        output_path.parent.mkdir(exist_ok=True, parents=True)
        simulator.save_result(output_path)
    else:
        save_archive(simulator, output_path, args.graph, args.model_config)


def cli():
    with timer("Simulation time:", 3):
        main(parse_args())

    log_memory()


if __name__ == "__main__":
    cli()
