import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

from .utils import log_memory, timer


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("-l", "--loglevel", default="info")

    return parser.parse_args()


def main(args: Namespace):
    logging.basicConfig(
        level=args.loglevel.upper(),
        format="[%(levelname)s] %(message)s",
    )


def cli():
    with timer("Simulation time", 3):
        main(parse_args())

    log_memory()


if __name__ == "__main__":
    cli()
