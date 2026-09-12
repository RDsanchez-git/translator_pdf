"""Guard de traduccion de excepciones a exit codes (D4, NADR-24 R19).

Patron production-grade: main() -> int en cada entry point; este guard traduce
excepciones no capturadas a categoria (c) con mensaje indexable. Los tests
assertean el int que retorna main() sin subprocess ni capturar SystemExit.
"""
from __future__ import annotations

import sys
from typing import Callable, NoReturn

import logging

from core.shared.errors import IndexedError
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from core.utils.logger import setup_logger

setup_logger()  # Inicializa el logger raíz global con JsonFormatter
logger = logging.getLogger(__name__)


def run_entry(main_fn: Callable[[], int]) -> NoReturn:
    """Ejecuta main_fn y traduce toda excepcion a exit code de categoria (c)."""
    try:
        sys.exit(main_fn() or EXIT_OK)
    except IndexedError as e:
        logger.critical("[%s] %s", e.code, e.message)
        sys.exit(EXIT_EXECUTION_FAILURE)
    except Exception as e:  # R19: stack traces sin traduccion no son mecanismo primario
        logger.critical("[UNEXPECTED-001] %s", e)
        sys.exit(EXIT_EXECUTION_FAILURE)
