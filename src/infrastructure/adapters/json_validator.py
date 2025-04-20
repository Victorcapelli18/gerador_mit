from jsonschema import validate, ValidationError
from typing import Any, Tuple


def validar_json(json_data: Any, schema: dict) -> Tuple[bool, ValidationError | None]:
    try:
        validate(instance=json_data, shcema=schema)
        return True, None
    except ValidationError as e:
        return False, e