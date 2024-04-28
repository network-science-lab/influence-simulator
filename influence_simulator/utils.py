import resource
from contextlib import contextmanager
from datetime import timedelta
from logging import getLogger
from time import perf_counter


logger = getLogger("influence-simulator")


def format_delta(seconds: float, digits: int = -1) -> str:
    """
    Formats time delta with given precision.
    """
    delta = str(timedelta(seconds=seconds))

    if "." in delta:
        if digits == 0:
            delta = delta.split(".", 1)[0]
        elif digits > 0:
            # format microseconds
            delta = delta.split(".")
            delta[1] = delta[1][:digits]
            delta = ".".join(delta)

    return delta


@contextmanager
def timer(message: str = "Time elapsed:", digits: int = -1):
    """
    Context manager based timer.
    """

    start = perf_counter()
    yield
    stop = perf_counter()

    delta = format_delta(seconds=(stop - start), digits=digits)

    logger.info(f"{message} {delta}")


def log_memory():
    memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

    logger.info(f"Memory used: {memory:_.2f} MiB")
