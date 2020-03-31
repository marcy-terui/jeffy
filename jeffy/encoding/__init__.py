from abc import ABC, abstractmethod

from typing import Any

class Encoding(ABC):

    @abstractmethod
    def encode(self, payload: Any) -> bytes:
        pass

    @abstractmethod
    def decode(self, payload: bytes) -> Any:
        pass


class DecodeError(Exception): pass
