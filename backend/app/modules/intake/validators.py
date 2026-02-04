"""
Intake Module - Validators
Funciones de validación específicas
"""

from typing import Any, Dict, List

from .schemas import InputType, QuestionDefinition


def validate_not_null(value: Any) -> bool:
    """Verifica que el valor no sea null o equivalente"""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() in ["", "null", "no_se", "none"]:
        return False
    return True


def validate_input_type(value: Any, expected_type: InputType) -> bool:
    """Verifica que el valor corresponda al tipo esperado"""
    if expected_type == InputType.BOOLEAN:
        return isinstance(value, bool)
    elif expected_type == InputType.ENUM:
        return isinstance(value, str)
    elif expected_type == InputType.MULTI_SELECT:
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    elif expected_type == InputType.RANGE:
        return isinstance(value, (int, float))
    elif expected_type == InputType.ROLE_SELECTOR:
        return isinstance(value, str)
    return False


def validate_enum_option(value: str, options: List[str]) -> bool:
    """Verifica que el valor esté en las opciones permitidas"""
    return value in options


def validate_multi_select_options(values: List[str], options: List[str]) -> List[str]:
    """Retorna lista de valores inválidos en multi-select"""
    return [v for v in values if v not in options]


def validate_range(value: float, min_val: float | None, max_val: float | None) -> bool:
    """Verifica que el valor esté dentro del rango"""
    if min_val is not None and value < min_val:
        return False
    if max_val is not None and value > max_val:
        return False
    return True


def validate_question_answer(
    question: QuestionDefinition,
    answer: Any
) -> Dict[str, Any]:
    """
    Valida una respuesta contra su definición de pregunta.
    Retorna dict con resultado y errores si los hay.
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    # Verificar requerido
    if question.required and not validate_not_null(answer):
        result["valid"] = False
        result["errors"].append(f"Campo '{question.id}' es requerido")
        return result

    # Si no hay respuesta y no es requerido, está ok
    if answer is None:
        return result

    # Verificar tipo
    if not validate_input_type(answer, question.input_type):
        result["valid"] = False
        result["errors"].append(
            f"Campo '{question.id}' debe ser de tipo {question.input_type.value}"
        )
        return result

    # Validaciones específicas por tipo
    if question.input_type == InputType.ENUM:
        if question.options and not validate_enum_option(answer, question.options):
            result["valid"] = False
            result["errors"].append(
                f"Valor '{answer}' no es una opción válida para '{question.id}'"
            )

    elif question.input_type == InputType.MULTI_SELECT:
        if question.options:
            invalid = validate_multi_select_options(answer, question.options)
            if invalid:
                result["valid"] = False
                result["errors"].append(
                    f"Valores inválidos en '{question.id}': {invalid}"
                )

    elif question.input_type == InputType.RANGE:
        if not validate_range(answer, question.range_min, question.range_max):
            result["valid"] = False
            result["errors"].append(
                f"Valor fuera de rango en '{question.id}': "
                f"debe estar entre {question.range_min} y {question.range_max}"
            )

    return result
