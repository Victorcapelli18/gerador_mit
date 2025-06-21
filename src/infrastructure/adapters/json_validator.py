from jsonschema import validate, ValidationError
from typing import Any, Tuple

def validar_json(json_data: Any, schema: dict) -> Tuple[bool, ValidationError | None]:
    """
    Valida um JSON contra um schema JSON.

    :param json_data: O JSON a ser validado.
    :param schema: O schema JSON contra o qual validar.
    :return: Uma tupla contendo um booleano indicando se a validação foi bem-sucedida e um erro de validação, se houver.
    """
    try:
        validate(instance=json_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, e