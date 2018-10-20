import functools
import logging
from typing import Any, Callable

framework = None


class Jeffy(object):

    def __init__(
        self,
        logger: logging.Logger,
        enable_event_logging: bool = True,
        enable_result_logging: bool = True
    ):
        self.logger = logger
        self.enable_event_logging = enable_event_logging
        self.enable_result_logging = enable_result_logging

    def log(self, msg: Any, level: int =logging.INFO) -> None:
        self.logger.log(level, msg)

    def _event_log(self, msg: Any) -> None:
        if self.enable_event_logging is True:
            self.log(msg)

    def general_event_handler(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(event: dict, context: Any) -> Any:
            self._event_log(event)
            try:
                result = func(event, context)
            except Exception as e:
                self.logger.exception(str(e))
                raise e
            self.logger.info(result)
            return result
        return wrapper


def setup(**kwargs: dict) -> Jeffy:
    """
    Setup Jeffy framework

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
