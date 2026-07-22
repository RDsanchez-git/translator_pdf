from typing import List

class TreeDistanceTable:
    """
    Matriz global persistente TD (Tree Distance) de Zhang-Shasha.
    Estructura optimizada en memoria con acceso de baja latencia.
    """
    __slots__ = ("_rows", "_cols", "_cells")

    def __init__(self, rows: int, cols: int, fill: float = 0.0):
        self._rows = rows
        self._cols = cols
        self._cells: List[List[float]] = [[fill] * cols for _ in range(rows)]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def cells(self) -> List[List[float]]:
        """Expone el buffer de lectura/escritura O(1) manteniendo la inmutabilidad de la referencia."""
        return self._cells