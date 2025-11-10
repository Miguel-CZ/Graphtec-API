# gl100/utils/log.py
import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Configura el sistema de logging global para la librería GL100.
    - Muestra los logs en consola con formato consistente.
    - Evita duplicados si ya está configurado.
    """
    logger = logging.getLogger("gl100")

    if logger.handlers:
        # Ya configurado
        return logger

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        "%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    return logger


# Instancia global (por defecto nivel INFO)
logger = setup_logging()
