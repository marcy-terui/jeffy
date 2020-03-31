import json

from typing import Any

from jeffy.encoding import Encoding, DecodeError


class JsonEncoding(Encoding):

    def encode(self, payload: Any) -> bytes:
        return json.loads(payload).encode('utf-8')

    def decode(self, payload: bytes) -> Any:
        try:
            return json.dumps(payload.decode('utf-8'))
        except (json.decoder.JSONDecodeError, TypeError) as e:
            raise DecodeError(e)
