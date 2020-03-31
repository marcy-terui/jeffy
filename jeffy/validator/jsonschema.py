import jsonschema
from typing import Any, Dict

from jeffy.validator import Validator, ValidationError


class JsonSchemeValidator(Validator):

    def __init__(self, scheme: Dict):
        self.scheme = scheme

    def validate(self, data: Any):
        try:
            jsonschema.validate(data, self.scheme)
        except jsonschema.ValidationError as e:
            raise ValidationError(e)

