from pydantic import BaseModel, ValidationError

from shared.logger import get_logger

logger = get_logger()

def safe_validate_model[T: BaseModel](model_class: type[T], data: dict) -> tuple[T | None, ValidationError | None]:
    try:
        return model_class.model_validate(data), None
    except ValidationError as e:
        logger.error(f"Erro ao validar modelo {model_class.__name__}: {e}")
        return None, e
