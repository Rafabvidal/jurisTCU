import logging

_DEFAULT_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
_DEFAULT_LEVEL = logging.INFO


def get_logger(name: str | None = None, level: int = _DEFAULT_LEVEL) -> logging.Logger:
    """
    Retorna um logger padronizado para o projeto.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_DEFAULT_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
