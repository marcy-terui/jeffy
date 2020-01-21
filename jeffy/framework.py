from jeffy.decorators import Decorators
from jeffy.logger import Logger

framework = None


class Jeffy(object):
    """
    Jeffy framework main class.
    """

    def __init__(self):
        self.logger = Logger()
        self.decorator = Decorators(logger=self.logger)


def setup(**kwargs: dict) -> Jeffy:
    """
    Jeffy framework setup.

    Parameters
    ----------
    logger: logging.Logger
        Logger instance
    enable_event_logging: bool
        Enable event payload logging
    enable_result_logging: bool
        Enable result(return value of the functions) logging

    Returns
    -------
    framework : jeffy.framework.Jeffy
    """
    global framework
    if framework is None:
        framework = Jeffy(**kwargs)  # type: ignore
    return framework
