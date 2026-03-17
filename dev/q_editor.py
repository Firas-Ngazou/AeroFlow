from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QApplication

import sys
import numpy as np
from enum import Enum

class CursorState(Enum):
    DEFAULT = 0
    PEN = 1
    LOCKED = 2

@dataclass
class Vertex:
    position: QPoint

class QEditor(QWidget):
    def __init__(self, cursor_initial_state: CursorState, parent: QWidget = None):
        super().__init__(parent)

        # Initial setup
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)

        self._cursor_state = cursor_initial_state
        self._cell_width = 40

        # Saved data
        self._placed_vertices: list[Vertex] | None = None
        self._placed_vertices_nd: np.ndarray = np.array([])
        self._cached_grid = None # for optimization
        self._cached_polygons: list[QPainterPath] | None = None # QPainterPath for optimization

    def paintEvent(self, event):
        painter = QPainter(self)

        if self._cached_grid is not None:
            painter.drawPixmap(0, 0, self._cached_grid)

        self._draw_vertices(painter)
        self._draw_polygons(painter)

    def resizeEvent(self, event):
        self._draw_grid()

    def _draw_grid(self):
        self._cached_grid = QPixmap(self.size())
        background_color = QColor(34, 34, 34)
        self._cached_grid.fill(background_color)
        painter = QPainter(self._cached_grid)

        left = self.rect().left()
        right = self.rect().right()
        top = self.rect().top()
        bottom = self.rect().bottom()
        x = left
        y = top

        primary_pen = QPen(QColor(75, 75, 75, 75))
        primary_pen.setWidth(2)
        secondary_pen = QPen(QColor(75, 75, 75, 25))
        secondary_pen.setWidth(2)

        painter.setPen(primary_pen)
        self._draw_lines(painter, x, y, top, bottom, left, right)

        x = int(left + self._cell_width/2)
        y = int(top + self._cell_width/2)

        painter.setPen(secondary_pen)
        self._draw_lines(painter, x, y, top, bottom, left, right)

        painter.end()

    def _draw_lines(self, painter: QPainter, x: int, y: int,
                    top: int, bottom: int, left: int, right: int):
        while x < right: # (Vertical lines)
            painter.drawLine(x, top, x, bottom)
            x += self._cell_width
        while y < bottom: # (Horizontal lines)
            painter.drawLine(left, y, right, y)
            y += self._cell_width

    def _draw_vertices(self, painter: QPainter):
        ...

    def _draw_polygons(self, painter: QPainter):
        ...

    def mouseMoveEvent(self, event, /):
        match self._cursor_state:
            case CursorState.LOCKED:
                return
            case CursorState.DEFAULT:
                ...
            case CursorState.PEN:
                ...

    def mousePressEvent(self, event, /):
        match self._cursor_state:
            case CursorState.LOCKED:
                return
            case CursorState.DEFAULT:
                ...
            case CursorState.PEN:
                ...

    def mouseReleaseEvent(self, event, /):
        match self._cursor_state:
            case CursorState.LOCKED:
                return
            case CursorState.DEFAULT:
                ...
            case CursorState.PEN:
                ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QEditor(CursorState.DEFAULT)
    demo.show()
    sys.exit(app.exec())