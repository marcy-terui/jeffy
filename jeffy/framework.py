from jeffy.handlers import Handlers
from jeffy.settings import (
    Logging,
    RestApi
)

app = None


class Jeffy(object):
    """
    Jeffy framework main class.
    """

    def __init__(
        self,
        logging: Logging = Logging(),
        rest_api: RestApi = RestApi()):
        self.logger = logging.logger
        self.correlation_attr_name = logging.correlation_attr_name
        self.handlers = Handlers()
        self.correlation_id_header = rest_api.correlation_id_header
        self.correlation_id = ''


def get_app(**kwargs: dict) -> Jeffy:
    """
    Get Jeffy framework application.

    Parameters
    ----------
    logging: jeffy.settings.Logging
        Logging settings
    http_api: jeffy.settings.RestApi
        Logging settings

    Returns
    -------
    app : jeffy.framework.Jeffy
    """
    global app
    if app is None or len(kwargs) > 0:
        app = Jeffy(**kwargs)  # type: ignore
    return app
