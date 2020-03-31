from abc import ABC, abstractmethod

from typing import Any


class Validator(ABC):

    @abstractmethod
    def validate(self, data: Any):
        pass


class NoneValidator(Validator):

    def validate(self, data: Any):
        pass


class ValidationError(Exception): pass
