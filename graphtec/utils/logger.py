import logging
import sys

def setup_logging(level:int|str=logging.INFO, logfile=None):
    """
    Configura el sistema de logging para toda la librería GL100.
    """

    # ----------------------------------------
    # 1. Convertir nivel textual a logging.X
    # ----------------------------------------
    if isinstance(level, str):
        level = level.upper()
        level = getattr(logging, level, logging.INFO)

    # Logger raíz del paquete
    logger = logging.getLogger("graphtec")

    # ----------------------------------------
    # 2. Configurar root logger para evitar ruido
    # ----------------------------------------
    logging.getLogger().setLevel(logging.WARNING)

    # ----------------------------------------
    # 3. Si ya tenía handlers, solo actualiza nivel
    # ----------------------------------------
    if logger.handlers:
        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)
        return logger

    # ----------------------------------------
    # 4. Crear handler de consola
    # ----------------------------------------
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        "%H:%M:%S",
    )
    console.setFormatter(formatter)

    logger.addHandler(console)

    # ----------------------------------------
    # 5. (Opcional) Handler de archivo
    # ----------------------------------------
    if logfile is not None:
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # ----------------------------------------
    # 6. Aplicar nivel y evitar duplicados
    # ----------------------------------------
    logger.setLevel(level)
    logger.propagate = False  # evita ruido desde root

    return logger
