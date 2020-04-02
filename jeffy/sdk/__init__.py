import logging
import json
from jeffy.framework import get_app


class SdkBase():
    """
    Jeffy SDK base class.
    """
    def __init__(self):
        self.app = get_app()
