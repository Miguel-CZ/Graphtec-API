# gl100/utils/__init__.py
"""
Utilidades comunes del paquete GL100
====================================

Incluye herramientas de soporte usadas por todos los módulos:
- Logging unificado
- Funciones auxiliares
"""

from gl100.utils.log import logger, setup_logging

__all__ = ["logger", "setup_logging"]
