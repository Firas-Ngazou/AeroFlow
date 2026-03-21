import math
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize, QLineF, QLine
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QBrush, QPainterPath, QPolygonF
from PySide6.QtWidgets import QWidget, QApplication

import sys
import numpy as np
from enum import Enum

from sympy.physics.quantum.gate import normalized


# NOTE: Gotta make the shapes re-position properly when the window is resized

class StateManager:


    class MouseState(Enum):
        # Design flaw: holding MB1 and MB2 at the same time is not possible :(
        DEFAULT = 0
        HOLDING_MB1 = 1
        HOLDING_MB2 = 2
        HOLDING_MB3 = 3


    class MouseLocation(Enum):
        DEFAULT = 0
        OVER_VERTEX = 1
        OVER_SHAPE = 2


    class CursorState(Enum):
        DEFAULT = 0
        PEN = 1
        LOCKED = 2


    class ActionState(Enum):
        DEFAULT = 0
        SELECTING_VERTICES = 1
        MOVING_VERTEX = 2
        MOVING_VERTICES = 3


    class KeyState(Enum):
        DEFAULT = 0
        HOLDING_SHIFT = 1
        HOLDING_CTRL = 2


    def __init__(self):
        self._mouse_state = StateManager.MouseState.DEFAULT
        self._cursor_state = StateManager.CursorState.DEFAULT
        self._action_state = StateManager.ActionState.DEFAULT
        self._mouse_location = StateManager.MouseLocation.DEFAULT
        self._key_state = StateManager.KeyState.DEFAULT

    @property
    def mouse_state(self) -> MouseState:
        return self._mouse_state
    @mouse_state.setter
    def mouse_state(self, state: MouseState):
        self._mouse_state = state

    @property
    def cursor_state(self) -> CursorState:
        return self._cursor_state
    @cursor_state.setter
    def cursor_state(self, state: CursorState):
        self._cursor_state = state

    @property
    def action_state(self) -> ActionState:
        return self._action_state
    @action_state.setter
    def action_state(self, state: ActionState):
        self._action_state = state

    @property
    def mouse_location(self) -> MouseLocation:
        return self._mouse_location
    @mouse_location.setter
    def mouse_location(self, location: MouseLocation):
        self._mouse_location = location

    @property
    def key_state(self) -> KeyState:
        return self._key_state
    @key_state.setter
    def key_state(self, state: KeyState):
        self._key_state = state


@dataclass
class Vertex:


    class VertexState(Enum):
        DEFAULT = 0
        SELECTED = 1
        HOVERED = 2
        HELD = 3
        HOVERED_SELECTED = 4
        MEDIAN = 5


    position: QPoint
    state: VertexState = VertexState.DEFAULT
    index_position: int = -1

    def move(self, delta_x: int, delta_y: int):
        self.position.setX(self.position.x() + delta_x)
        self.position.setY(self.position.y() + delta_y)


class Shape:


    class ShapeState(Enum):
        DEFAULT = 0
        SELECTED = 1
        HOVERED = 2
        HOVERED_DELETE = 3


    class ShapeStatus(Enum):
        DEFAULT = 0
        CLOSED = 1


    def __init__(self, vertices: list[Vertex]):
        self._vertex_min_radius = 5
        self._vertex_max_radius = 7

        # States
        self._state = Shape.ShapeState.SELECTED
        self._status = Shape.ShapeStatus.DEFAULT

        # Vertices
        self._vertices = vertices
        self._vertices_nd = np.empty((0, 2), dtype=int)
        self._update_vertices_nd()

        # Path
        self._path: QPainterPath | None = None # QPainterPath for not having to re-make a QPolygonF every time

        # Categories
        self._categories = {state: [] for state in Vertex.VertexState}
        self._update_categories()

        # Settings
        self._hide_vertices = False

        # Median positions
        self._median_vertices: list[Vertex] | None = None # The positions in between the vertices
        self._median_vertices_nd: np.ndarray | None = None
        self._current_median: Vertex | None = None
        self._current_median_path: QPainterPath | None = None

        # region Pens and brushes
        self._default_vertex_pen = QPen(QColor(179, 208, 255))  # light blue
        self._default_vertex_pen.setWidth(2)
        self._selected_vertex_pen = QPen(QColor(77, 142, 255))  # dark blue
        self._selected_vertex_pen.setWidth(4)
        self._hovered_vertex_pen = QPen(QColor(179, 208, 255))  # light blue
        self._hovered_vertex_pen.setWidth(2)
        self._held_vertex_pen = QPen(QColor(77, 142, 255))  # dark blue
        self._held_vertex_pen.setWidth(4)
        self._hovered_selected_vertex_pen = QPen(QColor(77, 142, 255))  # dark blue
        self._hovered_selected_vertex_pen.setWidth(4)

        self._default_vertex_brush = QBrush(QColor(245, 245, 245))  # white
        self._selected_vertex_brush = QBrush(QColor(245, 245, 245))  # white
        self._hovered_vertex_brush = QBrush(QColor(204, 204, 204))  # light gray
        self._held_vertex_brush = QBrush(QColor(171, 171, 171))  # dark gray
        self._hovered_selected_vertex_brush = QBrush(QColor(204, 204, 204))  # light gray

        self._shape_pen = QPen(QColor(245, 245, 245))
        self._shape_pen.setWidth(2)
        self._shape_brush = QBrush(QColor(220, 220, 220, 100))
        self._shape_hover_pen = QPen(QColor(0, 124, 217))
        self._shape_hover_pen.setWidth(4)
        self._shape_hover_brush = QBrush(QColor(119, 197, 255, 100))
        self._shape_hover_delete_pen = QPen(QColor(225, 0, 0))
        self._shape_hover_delete_pen.setWidth(4)
        self._shape_hover_delete_brush = QBrush(QColor(225, 0, 0, 100))

        self._median_vertex_pen = QPen(QColor(179, 208, 255))
        self._median_vertex_pen.setWidth(4)
        self._median_vertex_brush = QBrush(QColor(179, 208, 255))
        # endregion

    #region Painting Logic
    def draw(self, painter: QPainter):
        if self._path is None: self._update_path()
        if self._state == Shape.ShapeState.HOVERED:
            painter.setPen(self._shape_hover_pen)
            painter.setBrush(self._shape_hover_brush)
        elif self._state == Shape.ShapeState.HOVERED_DELETE:
            painter.setPen(self._shape_hover_delete_pen)
            painter.setBrush(self._shape_hover_delete_brush)
        else:
            painter.setPen(self._shape_pen)
            painter.setBrush(self._shape_brush)

        if self._status == Shape.ShapeStatus.CLOSED:
            self._path.closeSubpath()
        painter.drawPath(self._path)

        if not self._hide_vertices: self._draw_vertices(painter)

    def _draw_vertices(self, painter: QPainter):
        if self._vertices:
            painter.setPen(self._default_vertex_pen)
            painter.setBrush(self._default_vertex_brush)
            for vertex in self._categories[Vertex.VertexState.DEFAULT]:
                painter.drawEllipse(vertex.position, self._vertex_min_radius, self._vertex_min_radius)

            painter.setPen(self._selected_vertex_pen)
            painter.setBrush(self._selected_vertex_brush)
            for vertex in self._categories[Vertex.VertexState.SELECTED]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

            painter.setPen(self._hovered_vertex_pen)
            painter.setBrush(self._hovered_vertex_brush)
            for vertex in self._categories[Vertex.VertexState.HOVERED]:
                painter.drawEllipse(vertex.position, self._vertex_min_radius, self._vertex_min_radius)

            painter.setPen(self._held_vertex_pen)
            painter.setBrush(self._held_vertex_brush)
            for vertex in self._categories[Vertex.VertexState.HELD]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

            painter.setPen(self._hovered_selected_vertex_pen)
            painter.setBrush(self._hovered_selected_vertex_brush)
            for vertex in self._categories[Vertex.VertexState.HOVERED_SELECTED]:
                painter.drawEllipse(vertex.position, self._vertex_max_radius, self._vertex_max_radius)

            painter.setPen(self._median_vertex_pen)
            painter.setBrush(self._median_vertex_brush)
            if self._current_median is not None:
                painter.drawPath(self._current_median_path)
    #endregion

    #region Vertex Addition
    def add_point(self, position: QPoint):
        if self._status == Shape.ShapeStatus.CLOSED: return
        # Unselecting all vertices
        self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)

        # Adding the vertex to the shape at the end of the lists
        self._vertices.append(Vertex(position=position, state=Vertex.VertexState.SELECTED,
                                     index_position=len(self._vertices)))
        self._vertices_nd = np.append(self._vertices_nd, [[position.x(), position.y()]], axis=0)

        self._update_categories()
        self._update_path()

    def add_median_vertex(self):
        if not self._current_median or self._status != Shape.ShapeStatus.CLOSED: return
        self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)
        self._current_median.state = Vertex.VertexState.SELECTED

        self._vertices.insert(self._current_median.index_position + 1, self._current_median)
        self._current_median.index_position = len(self._vertices) - 1

        for i, vertex in enumerate(self._vertices):
            vertex.index_position = i

        self._current_median = None

        self._update_vertices_nd()
        self._update_categories()
        self._update_path()
    #endregion

    #region Vertex Manipulation
    def unselect_path(self):
        self._status = Shape.ShapeStatus.CLOSED
        self._state = Shape.ShapeState.DEFAULT
        self.reset_selected_vertices()
        self._update_path()
        self._hide_vertices = True

    def select_path(self):
        self._state = Shape.ShapeState.SELECTED
        self._hide_vertices = False

    def move_held_vertices(self, delta_x: int, delta_y: int):
        for vertex in self._categories[Vertex.VertexState.HELD]:
            vertex.move(delta_x, delta_y)
            self._update_vertices_nd(vertex.index_position)
        self._update_path()

    def move_held_vertices_to_point(self, position: QPoint):
        for vertex in self._categories[Vertex.VertexState.HELD]:
            vertex.position = position
            self._update_vertices_nd(vertex.index_position)
        self._update_path()

    def select_content(self, area: QRect):
        for vertex in self._vertices:
            if area.contains(vertex.position):
                self.select_vertex(vertex, unselect_others=False)

    def hold_selection(self):
        for vertex in self._categories[Vertex.VertexState.SELECTED]:
            self.hold_vertex(vertex)
    #endregion

    #region State Manipulation
    def hover_vertex(self, vertex: Vertex):
        match vertex.state:
            case Vertex.VertexState.DEFAULT:
                vertex.state = Vertex.VertexState.HOVERED
            case Vertex.VertexState.SELECTED:
                vertex.state = Vertex.VertexState.HOVERED_SELECTED
        self._update_categories()

    def select_vertex(self, vertex: Vertex, unselect_others: bool = False):
        if unselect_others: self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)
        vertex.state = Vertex.VertexState.SELECTED
        self._update_categories()

    def hold_vertex(self, vertex: Vertex, unselect_others: bool = False):
        if unselect_others: self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)
        vertex.state = Vertex.VertexState.HELD
        self._update_categories()

    def release_all(self):
        for vertex in self._categories[Vertex.VertexState.HELD]:
            vertex.state = Vertex.VertexState.SELECTED
        self._update_categories()

    def reset_selected_vertices(self):
        self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)
        self._update_categories()

    def reset_hovered_vertices(self):
        self._switch_category_state(Vertex.VertexState.HOVERED, Vertex.VertexState.DEFAULT)
        self._switch_category_state(Vertex.VertexState.HOVERED_SELECTED, Vertex.VertexState.SELECTED)
        self._update_categories()
    #endregion

    def is_over_shape(self, position: QPoint) -> bool:
        self._state = Shape.ShapeState.DEFAULT
        if self._path.contains(position):
            return True
        return False

    def highlight(self, for_deletion: bool = False):
        if for_deletion:
            self._state = Shape.ShapeState.HOVERED_DELETE
            return
        self._state = Shape.ShapeState.HOVERED

    def delete_selected_vertices(self):
        if not self._vertices: return
        self._vertices = [vertex for vertex in self._vertices if vertex.state != (Vertex.VertexState.SELECTED or
                                                                              Vertex.VertexState.HOVERED_SELECTED)]
        for new_index, vertex in enumerate(self._vertices):
            vertex.index_position = new_index

        self._update_vertices_nd()
        self._update_categories()
        self._update_path()

    def translate(self, delta_x: int, delta_y: int):
        if not self._vertices: return
        for vertex in self._vertices:
            vertex.position += QPoint(delta_x, delta_y)
        self._vertices_nd += np.array([[delta_x, delta_y]]*self._vertices_nd.shape[0], dtype=int)
        self._update_path()

    def is_in_delete_rect(self, rect: QRect) -> bool:
        self._state = Shape.ShapeState.DEFAULT
        x_coords = self._vertices_nd[:, 0]
        y_coords = self._vertices_nd[:, 1]

        normalized_rect = rect.normalized()

        left, top, right, bottom = normalized_rect.getCoords()
        inside_x = (left <= x_coords) & (x_coords <= right)
        inside_y = (top <= y_coords) & (y_coords <= bottom)

        if np.any(inside_x & inside_y):
            self._state = Shape.ShapeState.HOVERED_DELETE
            return True
        return False

    #region Near Vertex Logic
    def near_vertex(self, position: QPoint) -> Vertex | None:
        return self._near_point(position, self._vertices_nd, self._vertices)

    def update_near_median(self, position: QPoint):
        if self._median_vertices is None: return
        median = self._near_point(position, self._median_vertices_nd, self._median_vertices)
        if median:
            median.state = Vertex.VertexState.MEDIAN
            self._current_median = median

            # Visuals
            self._current_median_path = QPainterPath()
            cross_line_length = 7
            cross_line_1 = QLine(QPoint(median.position.x() - cross_line_length // 2,
                                        median.position.y() - cross_line_length // 2),
                                 QPoint(median.position.x() + cross_line_length // 2,
                                        median.position.y() + cross_line_length // 2))
            cross_line_2 = QLine(QPoint(median.position.x() - cross_line_length // 2,
                                        median.position.y() + cross_line_length // 2),
                                 QPoint(median.position.x() + cross_line_length // 2,
                                        median.position.y() - cross_line_length // 2))
            self._current_median_path.moveTo(cross_line_1.p1())
            self._current_median_path.lineTo(cross_line_1.p2())
            self._current_median_path.moveTo(cross_line_2.p1())
            self._current_median_path.lineTo(cross_line_2.p2())

        else:
            self._current_median = None

    def _near_point(self, position: QPoint, nd_data: np.ndarray, vertices_data: list[Vertex]) -> Vertex | None:
        if nd_data.size < 1: return None
        target_pos = np.array([position.x(), position.y()])
        distances = np.linalg.norm(nd_data - target_pos, axis=1)
        nearest_index = np.argmin(distances)
        nearest_pos = distances[nearest_index]

        if nearest_pos < self._vertex_max_radius:
            return vertices_data[nearest_index]
        return None
    #endregion

    #region Update Methods
    def _update_categories(self):
        for state in Vertex.VertexState:
            self._categories[state] = []
        for vertex in self._vertices:
            self._categories[vertex.state].append(vertex)

    def _update_path(self):
        self._update_median_positions()
        qt_points = [QPoint(x, y) for x, y in self._vertices_nd]
        polygon = QPolygonF(qt_points)
        path = QPainterPath()
        path.addPolygon(polygon)
        self._path: QPainterPath = path

    def _update_vertices_nd(self, index_position: int = None):
        if not self._vertices:
            self._vertices_nd = np.empty((0, 2), dtype=int)
            return

        if index_position is not None:
            self._vertices_nd[index_position] = [self._vertices[index_position].position.x(), self._vertices[index_position].position.y()]
            return

        self._vertices_nd = np.array([[vertex.position.x(), vertex.position.y()] for vertex in self._vertices],
                                     dtype=int)

    def _update_median_positions(self):
        # Currently updating the whole median list, even when not needed.
        if not self._vertices or len(self._vertices) < 2:
            self._median_vertices = None
            return

        self._median_vertices = None
        for i, vertex in enumerate(self._vertices):
            right_vert = self._vertices[i + 1] if i + 1 < len(self._vertices) else self._vertices[0]
            left_vert = vertex

            delta_x = right_vert.position.x() - left_vert.position.x()
            delta_y = right_vert.position.y() - left_vert.position.y()
            median_vertex = Vertex(position=QPoint(left_vert.position.x() + delta_x // 2,
                                                   left_vert.position.y() + delta_y // 2),
                                   state=Vertex.VertexState.MEDIAN,
                                   index_position=vertex.index_position)
            if i == 0: self._median_vertices = [median_vertex]
            else: self._median_vertices.append(median_vertex)

        self._median_vertices_nd = np.array([[vertex.position.x(), vertex.position.y()]
                                            for vertex in self._median_vertices])
    #endregion

    def _switch_category_state(self, category: Vertex.VertexState, state: Vertex.VertexState):
        for vertex in self._categories[category]:
            vertex.state = state

    @property
    def selected_vertices(self) -> list[Vertex]:
        return self._categories[Vertex.VertexState.SELECTED]

    @property
    def vertices(self) -> list[Vertex]:
        return self._vertices

    @property
    def current_median(self) -> list[QPoint] | None:
        return  self._current_median


class QEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)

        self._state_manager = StateManager()

        # Shapes
        self._shapes: list[Shape] = []
        self._current_shape: Shape | None = None
        self._nearest_shape: Shape | None = None
        self._shapes_to_remove: list[Shape] | None = None

        # Grid
        self._cell_width = 40
        self._cached_grid: QPixmap | None = None

        # Selection
        self._selecting_rect: QRect | None = None
        self._selected_rect: QRect | None = None
        self._select_start_pos: QPoint | None = None

        #region Pens and brushes
        self._selecting_rect_pen = QPen(QColor(0, 124, 217))
        self._selecting_rect_pen.setWidth(2)
        self._selection_rect_brush = QBrush(QColor(119, 197, 255, 100))
        self._deleting_rect_pen = QPen(QColor(245, 0, 0))
        self._deleting_rect_pen.setWidth(2)
        self._deleting_rect_brush = QBrush(QColor(245, 0, 0, 100))

        self._selected_rect_pen = QPen(QColor(245, 245, 245))
        self._selected_rect_pen.setWidth(2)
        #endregion

    #region Painting Events
    def paintEvent(self, event):
        painter = QPainter(self)

        if self._cached_grid is not None:
            painter.drawPixmap(0, 0, self._cached_grid)

        self._draw_shapes(painter)
        self._draw_selection_rects(painter)

        painter.end()

    def resizeEvent(self, event):
        self._draw_grid()

        if not event.oldSize().isValid(): return

        delta_width = event.size().width() - event.oldSize().width()
        delta_height = event.size().height() - event.oldSize().height()

        delta_x = delta_width // 2
        delta_y = delta_height // 2

        # When resizing to many times, since it gets the // of the deltas, the shapes do move a little bit more than
        # they should. Meh... Ig it's fine.
        for shape in self._shapes:
            shape.translate(delta_x, delta_y)

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

    def _draw_shapes(self, painter: QPainter):
        for shape in self._shapes:
            shape.draw(painter)

    def _draw_selection_rects(self, painter: QPainter):
        if self._selecting_rect is not None:

            # Red rect if the user is holding down the ctrl key
            if self._state_manager.key_state == StateManager.KeyState.HOLDING_CTRL:
                painter.setPen(self._deleting_rect_pen)
                painter.setBrush(self._deleting_rect_brush)

            # Blue rect if the user is not holding down the ctrl key
            else:
                painter.setPen(self._selecting_rect_pen)
                painter.setBrush(self._selection_rect_brush)
            painter.drawRect(self._selecting_rect)

        # White rect around the selected vertices
        elif self._selected_rect is not None:
            painter.setPen(self._selected_rect_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selected_rect)
    #endregion

    #region Input Events
    def mouseMoveEvent(self, event, /):
        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                position = event.position().toPoint()

                if self._current_shape is None:
                    self._state_manager.mouse_location = StateManager.MouseLocation.DEFAULT
                    if not self._state_manager.action_state == StateManager.ActionState.SELECTING_VERTICES:
                        self._nearest_shape = None

                        for shape in self._shapes:

                            # Mouse is hovering over a shape
                            if shape.is_over_shape(position):
                                self._state_manager.mouse_location = StateManager.MouseLocation.OVER_SHAPE
                                self._nearest_shape = shape

                        # Highlight the last shape that was detected as hovered
                        if self._nearest_shape is not None: self._nearest_shape.highlight()
                    elif self._state_manager.key_state == StateManager.KeyState.HOLDING_CTRL:
                        # Mouse is selecting shapes to delete
                        self._shapes_to_remove = None
                        if self._selecting_rect is not None:
                            for shape in self._shapes:
                                if shape.is_in_delete_rect(self._selecting_rect):
                                    if self._shapes_to_remove is not None:
                                        self._shapes_to_remove.append(shape)
                                    else:
                                        self._shapes_to_remove = [shape]
                                    shape.highlight(for_deletion=True)

                            self._selecting_rect.setBottomRight(position)

                    self.update()
                    return

                # Mouse buttons are not pressed
                if self._state_manager.mouse_state == StateManager.MouseState.DEFAULT:
                    near_vertex = self._current_shape.near_vertex(position)

                    # Mouse is hovering over a vertex
                    if near_vertex is not None:
                        self._state_manager.mouse_location = StateManager.MouseLocation.OVER_VERTEX
                        self._current_shape.hover_vertex(near_vertex)

                    # Mouse is not hovering over a vertex
                    else:
                        self._state_manager.mouse_location = StateManager.MouseLocation.DEFAULT
                        if self._selected_rect is None: self._current_shape.update_near_median(position)
                        self._current_shape.reset_hovered_vertices()

                # Mouse left button is pressed
                elif self._state_manager.mouse_state == StateManager.MouseState.HOLDING_MB1:

                    # Mouse is moving a vertex
                    if self._state_manager.action_state == StateManager.ActionState.MOVING_VERTEX:
                        self._current_shape.move_held_vertices_to_point(position)

                    # Mouse is moving vertices
                    elif self._state_manager.action_state == StateManager.ActionState.MOVING_VERTICES:
                        self._current_shape.move_held_vertices(position.x() - self._select_start_pos.x(),
                                                               position.y() - self._select_start_pos.y())
                        self._select_start_pos = position
                        self._update_selected_rect()

                    # Mouse is selecting vertices
                    elif self._state_manager.action_state == StateManager.ActionState.SELECTING_VERTICES:
                        self._selecting_rect.setBottomRight(position)
                        self._current_shape.select_content(self._selecting_rect)

            case StateManager.CursorState.PEN:
                ...

        self.update()

    def mousePressEvent(self, event, /):
        # temp stuff ?? (maybe not actually...)
        if event.button() == Qt.MouseButton.RightButton:
            if self._state_manager.cursor_state == StateManager.CursorState.DEFAULT:
                self.switch_cursor(StateManager.CursorState.PEN)
            else:
                self.switch_cursor(StateManager.CursorState.DEFAULT)
        if event.button() == Qt.MouseButton.MiddleButton:
            print(f"Cursor State: {self._state_manager.cursor_state}\nMouse Location: {self._state_manager.mouse_location}"
                  f"\nAction State: {self._state_manager.action_state}\nNearest Shape: {self._nearest_shape}\n"
                  f"Current Shape: {self._current_shape}\n---------------------<")
        # ----

        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if event.button() == Qt.MouseButton.LeftButton:
                    position = event.position().toPoint()

                    if self._current_shape is None:

                        # Mouse is hovering over a shape, we select it
                        if self._state_manager.mouse_location == StateManager.MouseLocation.OVER_SHAPE:
                            self._state_manager.action_state = StateManager.ActionState.DEFAULT
                            self._current_shape = self._nearest_shape
                            self._current_shape.select_path()

                        # Mouse is not hovering over a shape, we start the building of the selecting rect
                        elif (self._state_manager.mouse_location == StateManager.MouseLocation.DEFAULT and
                              self._state_manager.key_state == StateManager.KeyState.HOLDING_CTRL):
                            self._state_manager.action_state = StateManager.ActionState.SELECTING_VERTICES
                            self._selecting_rect = QRect(position, position)
                        return

                    # Mouse left button is pressed
                    self._state_manager.mouse_state = StateManager.MouseState.HOLDING_MB1

                    # Mouse left button was pressed while over a vertex
                    if self._current_shape.near_vertex(position) is not None:
                        self._state_manager.action_state = StateManager.ActionState.MOVING_VERTEX
                        unselect_others = self._state_manager.key_state != StateManager.KeyState.HOLDING_SHIFT
                        self._current_shape.hold_vertex(self._current_shape.near_vertex(position),
                                                        unselect_others=unselect_others)

                    # Mouse left button was pressed while over a selection rectangle
                    elif self._selected_rect is not None and self._selected_rect.contains(position):
                        self._state_manager.action_state = StateManager.ActionState.MOVING_VERTICES
                        self._current_shape.hold_selection()
                        self._select_start_pos = position # Updates the position of the start of the delta (type shi)

                    # Mouse left button was pressed while near a median vertex
                    elif self._current_shape.current_median is not None:
                        self._current_shape.add_median_vertex()

                    # Mouse left button was pressed while floating
                    else:
                        self._state_manager.action_state = StateManager.ActionState.SELECTING_VERTICES
                        if not self._state_manager.key_state == StateManager.KeyState.HOLDING_SHIFT:
                            self._current_shape.reset_selected_vertices() # Unselect all currently selected vertices
                        self._selecting_rect = QRect(position, position) # The blue rectangle thing (or red for delete)

            case StateManager.CursorState.PEN:
                if event.button() == Qt.MouseButton.LeftButton:
                    position = event.position().toPoint()
                    if self._current_shape is None:
                        # Making a new shape
                        self._shapes.append(Shape([Vertex(position=position, state=Vertex.VertexState.SELECTED,
                                                         index_position=0)]))
                        self._current_shape = self._shapes[-1]
                    else:
                        # Adding a point to the current shape
                        near_vertex = self._current_shape.near_vertex(position)
                        if near_vertex is not None and near_vertex.index_position == 0:
                            self._exit_current_shape()
                        elif near_vertex is None:
                            self._current_shape.add_point(position)

        self.update()

    def mouseReleaseEvent(self, event, /):
        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if event.button() == Qt.MouseButton.LeftButton:

                    # Mouse left button was released
                    self._selecting_rect = None
                    if self._current_shape is not None: self._current_shape.release_all()
                    if self._state_manager.key_state != StateManager.KeyState.HOLDING_CTRL: self._update_selected_rect()
                    elif self._current_shape is not None:
                        # Deleting selection
                        self._selected_rect = None
                        self._current_shape.delete_selected_vertices()
                        if not self._current_shape.vertices:
                            self._shapes.remove(self._current_shape)
                            self._current_shape = None
                    else:
                        # Deleting a shape
                        self._selected_rect = None
                        if self._shapes_to_remove is not None:
                            for shape in self._shapes_to_remove:
                                self._shapes.remove(shape)

                    self._state_manager.mouse_state = StateManager.MouseState.DEFAULT
                    self._state_manager.action_state = StateManager.ActionState.DEFAULT

            case StateManager.CursorState.PEN:
                ...

        self.update()

    def keyPressEvent(self, event, /):
        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if event.key() == Qt.Key.Key_Control:
                    self._state_manager.key_state = StateManager.KeyState.HOLDING_CTRL
                elif event.key() == Qt.Key.Key_Shift:
                    self._state_manager.key_state = StateManager.KeyState.HOLDING_SHIFT

    def keyReleaseEvent(self, event, /):
        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if event.key() == Qt.Key.Key_Control or event.key() == Qt.Key.Key_Shift:
                    self._state_manager.key_state = StateManager.KeyState.DEFAULT
    #endregion

    def switch_cursor(self, cursor_state: StateManager.CursorState):
        self._state_manager.cursor_state = cursor_state
        self._selecting_rect = None
        self._selected_rect = None

        self._state_manager.action_state = StateManager.ActionState.DEFAULT
        self._state_manager.mouse_state = StateManager.MouseState.DEFAULT
        self._state_manager.mouse_location = StateManager.MouseLocation.DEFAULT
        self._state_manager.key_state = StateManager.KeyState.DEFAULT

        if self._current_shape is not None and cursor_state == StateManager.CursorState.PEN:
            self._exit_current_shape()

        self.update()

    def _update_selected_rect(self):
        if self._current_shape is None: return
        selected = self._current_shape.selected_vertices
        if not len(selected) > 1:
            self._selected_rect = None
            return

        highest = selected[0].position.y()
        lowest = selected[0].position.y()
        farthest_right = selected[0].position.x()
        farthest_left = selected[0].position.x()

        for vertex in selected:
            if vertex.position.y() < highest: highest = vertex.position.y()
            if vertex.position.y() > lowest: lowest = vertex.position.y()
            if vertex.position.x() > farthest_right: farthest_right = vertex.position.x()
            if vertex.position.x() < farthest_left: farthest_left = vertex.position.x()

        self._selected_rect = QRect(farthest_left, highest, farthest_right - farthest_left, lowest - highest)

    def _exit_current_shape(self):
        self._current_shape.unselect_path()
        self._current_shape = None

        self._state_manager.action_state = StateManager.ActionState.DEFAULT
        self._state_manager.mouse_state = StateManager.MouseState.DEFAULT
        self._state_manager.cursor_state = StateManager.CursorState.DEFAULT


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QEditor()
    demo.show()
    sys.exit(app.exec())