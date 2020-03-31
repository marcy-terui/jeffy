import json

from typing import Any

from jeffy.encoding import Encoding


class BytesEncoding(Encoding):

    def encode(self, payload: Any) -> bytes:
        return payload

    def decode(self, payload: bytes) -> Any:
        return payload
