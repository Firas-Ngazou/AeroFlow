from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QBrush, QPainterPath, QPolygonF
from PySide6.QtWidgets import QWidget, QApplication

import sys
import numpy as np
from enum import Enum

# NOTES: For optimization, maybe use numbers for states instead of words and vectorize the whole thing. -> For now, most
#        for-loops do not represent that big of a performance issue, but they may become one if the user chooses to
#        place and select multiple hundreds of vertices.
#
#        Maybe make a class QShape(QPainterPath)?

class CursorState(Enum):
    DEFAULT = 0
    PEN = 1
    LOCKED = 2

class VertexState(Enum):
    DEFAULT = 0
    SELECTED = 1
    HOVERED = 2
    HELD = 3
    HOVERED_SELECTED = 4

class MouseState(Enum):
    FLOATING = 0
    HOLDING_MB1_VERTEX = 1
    HOLDING_MB1_VERTICES = 2
    HOLDING_MB1_AIR = 3
    HOLDING_MB3 = 4

class KeyboardState(Enum):
    DEFAULT = 0
    HOLDING_SHIFT = 1

@dataclass
class Vertex:
    position: QPoint
    state: VertexState

class QEditor(QWidget):
    def __init__(self, cursor_initial_state: CursorState, parent: QWidget = None):
        super().__init__(parent)

        # Initial setup
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)

        self._cursor_state = cursor_initial_state
        self._cell_width = 40
        self._vertex_min_radius = 5
        self._vertex_max_radius = 7

        # Saved data
        self._placed_vertices: list[Vertex] = []
        self._categories = {state: [] for state in VertexState}
        self._placed_vertices_nd: np.ndarray = np.empty((0, 2), dtype=int)
        self._cached_grid = None # for optimization
        # self._shapes: list[list[QPoint]] = [[]]
        self._shapes_lengths: list[int] = []
        self._shape_index = 0
        self._cached_shapes: list[QPainterPath] = [] # QPainterPath for optimization
        self._selecting_rect: QRect | None = None
        self._selected_rect: QRect | None = None
        self._selected_move_start: QPoint | None = None

        # Mouse
        self._mouse_state = MouseState.FLOATING
        self._block_vertex_placement = False
        # self._near_vertex: Vertex | None = None
        self._near_vertex_index: int | None = None

        # Settings
        self._show_vertices = True

        #region Pens and brushes
        self._default_vertex_pen = QPen(QColor(179, 208, 255)) # light blue
        self._default_vertex_pen.setWidth(2)
        self._selected_vertex_pen = QPen(QColor(77, 142, 255)) # dark blue
        self._selected_vertex_pen.setWidth(4)
        self._hovered_vertex_pen = QPen(QColor(179, 208, 255)) # light blue
        self._hovered_vertex_pen.setWidth(2)
        self._held_vertex_pen = QPen(QColor(77, 142, 255)) # dark blue
        self._held_vertex_pen.setWidth(4)
        self._hovered_selected_vertex_pen = QPen(QColor(77, 142, 255)) # dark blue
        self._hovered_selected_vertex_pen.setWidth(4)

        self._default_vertex_brush = QBrush(QColor(245, 245, 245)) # white
        self._selected_vertex_brush = QBrush(QColor(245, 245, 245)) # white
        self._hovered_vertex_brush = QBrush(QColor(204, 204, 204)) # light gray
        self._held_vertex_brush = QBrush(QColor(171, 171, 171)) # dark gray
        self._hovered_selected_vertex_brush = QBrush(QColor(204, 204, 204)) # light gray

        self._polygon_pen = QPen(QColor(245, 245, 245))
        self._polygon_pen.setWidth(2)
        self._polygon_brush = QBrush(QColor(220, 220, 220, 100))

        self._selecting_rect_pen = QPen(QColor(0, 124, 217))
        self._selecting_rect_pen.setWidth(2)
        self._selection_rect_brush = QBrush(QColor(119, 197, 255, 100))

        self._selected_rect_pen = QPen(QColor(245, 245, 245))
        self._selected_rect_pen.setWidth(2)
        #endregion

    def paintEvent(self, event):
        painter = QPainter(self)

        if self._cached_grid is not None:
            painter.drawPixmap(0, 0, self._cached_grid)

        self._draw_polygons(painter)
        self._draw_vertices(painter)
        self._draw_selection_rects(painter)

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
        if self._placed_vertices and self._show_vertices:
            painter.setPen(self._default_vertex_pen)
            painter.setBrush(self._default_vertex_brush)
            for vertex in self._categories[VertexState.DEFAULT]:
                painter.drawEllipse(vertex.position, self._vertex_min_radius, self._vertex_min_radius)

            painter.setPen(self._selected_vertex_pen)
            painter.setBrush(self._selected_vertex_brush)
            for vertex in self._categories[VertexState.SELECTED]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

            painter.setPen(self._hovered_vertex_pen)
            painter.setBrush(self._hovered_vertex_brush)
            for vertex in self._categories[VertexState.HOVERED]:
                painter.drawEllipse(vertex.position, self._vertex_min_radius, self._vertex_min_radius)

            painter.setPen(self._held_vertex_pen)
            painter.setBrush(self._held_vertex_brush)
            for vertex in self._categories[VertexState.HELD]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

            painter.setPen(self._hovered_selected_vertex_pen)
            painter.setBrush(self._hovered_selected_vertex_brush)
            for vertex in self._categories[VertexState.HOVERED_SELECTED]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

    def _draw_polygons(self, painter: QPainter):
        if self._cached_shapes:
            for path in self._cached_shapes:
                painter.setPen(self._polygon_pen)
                painter.setBrush(self._polygon_brush)
                painter.drawPath(path)

    def _draw_selection_rects(self, painter: QPainter):
        if self._selecting_rect is not None:
            painter.setPen(self._selecting_rect_pen)
            painter.setBrush(self._selection_rect_brush)
            painter.drawRect(self._selecting_rect)
        elif self._selected_rect is not None:
            painter.setPen(self._selected_rect_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selected_rect)

    def mouseMoveEvent(self, event, /):
        match self._cursor_state:
            case CursorState.LOCKED:
                return

            case CursorState.DEFAULT:
                if self._placed_vertices is None: return
                pos = event.position().toPoint()
                if self._mouse_state == MouseState.FLOATING:
                    near_vertex_pos = self._find_near_vertex_point(pos)
                    if near_vertex_pos is not None:
                        vertex_index = self._get_vertex_index(near_vertex_pos)
                        self._near_vertex_index = vertex_index
                    else: self._near_vertex_index = None

                    self._update_hovered_states()
                elif self._mouse_state == MouseState.HOLDING_MB1_VERTEX:
                    if self.near_vertex.state is VertexState.HELD:
                        self._set_vertex_position(self._near_vertex_index, pos)
                elif self._mouse_state == MouseState.HOLDING_MB1_AIR:
                    self._selecting_rect.setBottomRight(pos)
                    self._update_selection_states()
                elif self._mouse_state == MouseState.HOLDING_MB1_VERTICES:
                    self._move_vertices(pos)
                    self._selected_move_start = pos

            case CursorState.PEN:
                ...

        self.update()

    def mousePressEvent(self, event, /):
        # temp stuff
        if event.button() == Qt.MouseButton.RightButton:
            if self._cursor_state == CursorState.DEFAULT:
                self._cursor_state = CursorState.PEN
            else:
                self._cursor_state = CursorState.DEFAULT
        # ----

        match self._cursor_state:
            case CursorState.LOCKED:
                return

            case CursorState.DEFAULT:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self._placed_vertices is None: return
                    if self.near_vertex is not None:
                        self._remove_selected_rect()
                        self._mouse_state = MouseState.HOLDING_MB1_VERTEX
                        self._change_category_state(VertexState.SELECTED, VertexState.DEFAULT)
                        self._placed_vertices[self._near_vertex_index].state = VertexState.HELD
                        self._update_shape(self._shape_index)
                    elif self._selected_rect is not None and self._selected_rect.contains(event.position().toPoint()):
                        self._mouse_state = MouseState.HOLDING_MB1_VERTICES
                        self._selected_move_start = event.position().toPoint()
                    else:
                        self._mouse_state = MouseState.HOLDING_MB1_AIR
                        self._remove_selected_rect()
                        self._selecting_rect = QRect(event.position().toPoint(), event.position().toPoint())
                        self._change_category_state(VertexState.SELECTED, VertexState.DEFAULT)

                    self._update_vertex_categories()

            case CursorState.PEN:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._change_category_state(VertexState.SELECTED, VertexState.DEFAULT)

                    if not len(self._shapes_lengths) < self._shape_index + 1:
                        self._shapes_lengths[self._shape_index] += 1
                    else: self._shapes_lengths.append(1)

                    self._add_vertex(event.position().toPoint())
                    self._update_vertex_categories()

        self.update()

    def mouseReleaseEvent(self, event, /):
        match self._cursor_state:
            case CursorState.LOCKED:
                return

            case CursorState.DEFAULT:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self.near_vertex is not None:
                        self._placed_vertices[self._near_vertex_index].state = VertexState.SELECTED
                    if self._mouse_state != MouseState.FLOATING:
                        self._mouse_state = MouseState.FLOATING
                        self._selecting_rect = None
                        self._update_selected_rect()

            case CursorState.PEN:
                ...

    def _find_near_vertex_point(self, position: QPoint) -> QPoint | None:
        if self._placed_vertices_nd.size == 0: return None

        target_pos = np.array([position.x(), position.y()])
        distances = np.linalg.norm(self._placed_vertices_nd - target_pos, axis=1)
        nearest_index = np.argmin(distances)
        nearest_pos = distances[nearest_index]

        if nearest_pos < self._vertex_max_radius:
            return QPoint(self._placed_vertices_nd[nearest_index, 0], self._placed_vertices_nd[nearest_index, 1])

        return None

    def _update_vertex_categories(self):
        for state in VertexState:
            self._categories[state] = []
        for vertex in self._placed_vertices:
            self._categories[vertex.state].append(vertex)

    def _get_vertex_index(self, position: QPoint) -> int:
        found = []
        index_pos = -1
        for vertex in self._placed_vertices:
            index_pos += 1
            if vertex.position == position:
                found.append(index_pos)

        match len(found):
            case 0:
                raise ValueError("No vertex found at given position: " + str(position))
            case 1:
                return found[0]
            case _:
                raise ValueError("Multiple vertices found at given position: " + str(position))

    def _update_hovered_states(self):
        if self._near_vertex_index is None:
            for vertex in self._categories[VertexState.HOVERED]:
                vertex.state = VertexState.DEFAULT
            for vertex in self._categories[VertexState.HOVERED_SELECTED]:
                vertex.state = VertexState.SELECTED
        else:
            if self.near_vertex.state == VertexState.SELECTED or self.near_vertex.state == VertexState.HOVERED_SELECTED:
                self._placed_vertices[self._near_vertex_index].state = VertexState.HOVERED_SELECTED
            else: self._placed_vertices[self._near_vertex_index].state = VertexState.HOVERED

        self._update_vertex_categories()

    def _update_selection_states(self):
        if self._selecting_rect is None: return

        for vertex in self._placed_vertices:
            if self._selecting_rect.contains(vertex.position):
                vertex.state = VertexState.SELECTED
            else: vertex.state = VertexState.DEFAULT

        self._update_vertex_categories()

    def _change_category_state(self, category: VertexState, state: VertexState):
        for vertex in self._categories[category]:
            vertex.state = state

    def _update_shape(self, index: int):
        # if len(self._shapes[index]) < 2: return

        shape_nd = self._placed_vertices_nd[0:self._shapes_lengths[index]]
        if len(shape_nd) < 2: return

        shape_qp = [QPoint(x, y) for x, y in shape_nd]
        polygon = QPolygonF(shape_qp)
        path = QPainterPath()
        path.addPolygon(polygon)

        if not len(self._cached_shapes) < index + 1:
            self._cached_shapes[index] = path
        else: self._cached_shapes.append(path)

    @property
    def near_vertex(self) -> Vertex | None:
        if self._near_vertex_index is None: return None
        return self._placed_vertices[self._near_vertex_index]

    def _set_vertex_position(self, index: int, world_position: QPoint):
        self._placed_vertices[index].position = world_position
        self._placed_vertices_nd[index] = [world_position.x(), world_position.y()]
        self._update_shape(self._shape_index)

    def _add_vertex(self, world_position: QPoint):
        self._placed_vertices.append(Vertex(world_position, VertexState.SELECTED))
        self._placed_vertices_nd = np.append(self._placed_vertices_nd, [[world_position.x(),
                                                                         world_position.y()]], axis=0)
        self._update_shape(self._shape_index)

    def _update_selected_rect(self):
        if not len(self._categories[VertexState.SELECTED]) > 1: return

        highest = self._categories[VertexState.SELECTED][0].position.y()
        lowest = self._categories[VertexState.SELECTED][0].position.y()
        farthest_right = self._categories[VertexState.SELECTED][0].position.x()
        farthest_left = self._categories[VertexState.SELECTED][0].position.x()

        for vertex in self._categories[VertexState.SELECTED]:
            if vertex.position.y() < highest: highest = vertex.position.y()
            if vertex.position.y() > lowest: lowest = vertex.position.y()
            if vertex.position.x() > farthest_right: farthest_right = vertex.position.x()
            if vertex.position.x() < farthest_left: farthest_left = vertex.position.x()

        self._selected_rect = QRect(farthest_left, highest, farthest_right - farthest_left, lowest - highest)

    def _move_vertices(self, world_position: QPoint):
        delta_x = world_position.x() - self._selected_move_start.x()
        delta_y = world_position.y() - self._selected_move_start.y()
        for vertex in self._categories[VertexState.SELECTED]:
            vertex.position.setX(vertex.position.x() + delta_x)
            vertex.position.setY(vertex.position.y() + delta_y)
            real_index = self._placed_vertices.index(vertex)
            self._placed_vertices_nd[real_index][0] += delta_x
            self._placed_vertices_nd[real_index][1] += delta_y
        self._update_selected_rect()
        self._update_shape(self._shape_index)

    def _remove_selected_rect(self):
        self._selected_rect = None
        self._selected_move_start = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QEditor(CursorState.PEN)
    demo.show()
    sys.exit(app.exec())