import logging
import sys


def get_logger(name: str, lvl=logging.DEBUG):
    lg = logging.getLogger(name)
    lg.setLevel(lvl)
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    lg.addHandler(handler)

    return lg
