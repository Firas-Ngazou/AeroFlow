from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QBrush, QPainterPath, QPolygonF
from PySide6.QtWidgets import QWidget, QApplication

import sys
import numpy as np
from enum import Enum

from dev.q_editor import VertexState

# Essentially the same as the last version, but with a lot cleaner code structure (better for future updates).

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


    class CursorState(Enum):
        DEFAULT = 0
        PEN = 1
        LOCKED = 2


    class ActionState(Enum):
        DEFAULT = 0
        SELECTING_VERTICES = 1
        MOVING_VERTEX = 2
        MOVING_VERTICES = 3


    def __init__(self):
        self._mouse_state = StateManager.MouseState.DEFAULT
        self._cursor_state = StateManager.CursorState.DEFAULT
        self._action_state = StateManager.ActionState.DEFAULT

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


@dataclass
class Vertex:


    class VertexState(Enum):
        DEFAULT = 0
        SELECTED = 1
        HOVERED = 2
        HELD = 3
        HOVERED_SELECTED = 4


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


    class ShapeStatus(Enum):
        DEFAULT = 0
        CLOSED = 1


    def __init__(self, vertices: list[Vertex]):
        self._vertex_min_radius = 5
        self._vertex_max_radius = 7

        self._state = Shape.ShapeState.SELECTED
        self._status = Shape.ShapeStatus.DEFAULT

        self._vertices = vertices
        self._vertices_nd = np.empty((0, 2), dtype=int)
        self._update_vertices_nd()

        self._path: QPainterPath | None = None # QPainterPath for not having to re-make a QPolygonF every time

        self._categories = {state: [] for state in Vertex.VertexState}
        self._update_categories()

        self._hide_vertices = False

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
        # endregion

    #region Painting Logic
    def draw(self, painter: QPainter):
        if self._path is None: self._update_path()
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
    #endregion

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

    def close_path(self):
        self._status = Shape.ShapeStatus.CLOSED
        self._state = Shape.ShapeState.DEFAULT
        self.reset_selected_vertices()
        self._hide_vertices = True

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
        self._switch_category_state(Vertex.VertexState.SELECTED, Vertex.VertexState.DEFAULT)
        for vertex in self._vertices:
            if area.contains(vertex.position):
                self.select_vertex(vertex)

    def hold_selection(self):
        for vertex in self._categories[Vertex.VertexState.SELECTED]:
            self.hold_vertex(vertex)

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

    def near_vertex(self, position: QPoint) -> Vertex | None:
        target_pos = np.array([position.x(), position.y()])
        distances = np.linalg.norm(self._vertices_nd - target_pos, axis=1)
        nearest_index = np.argmin(distances)
        nearest_pos = distances[nearest_index]

        if nearest_pos < self._vertex_max_radius:
            return self._vertices[nearest_index]

        return None

    def _switch_category_state(self, category: Vertex.VertexState, state: Vertex.VertexState):
        for vertex in self._categories[category]:
            vertex.state = state

    def _update_categories(self):
        for state in Vertex.VertexState:
            self._categories[state] = []
        for vertex in self._vertices:
            self._categories[vertex.state].append(vertex)

    def _update_path(self):
        qt_points = [QPoint(x, y) for x, y in self._vertices_nd]
        polygon = QPolygonF(qt_points)
        path = QPainterPath()
        path.addPolygon(polygon)
        self._path: QPainterPath = path

    def _update_vertices_nd(self, index_position: int = None):
        if self._status == Shape.ShapeStatus.CLOSED: return
        if not self._vertices:
            self._vertices_nd = np.empty((0, 2), dtype=int)
            return

        if index_position is not None:
            self._vertices_nd[index_position] = [self._vertices[index_position].position.x(), self._vertices[index_position].position.y()]
            return

        self._vertices_nd = np.array([[vertex.position.x(), vertex.position.y()] for vertex in self._vertices],
                                     dtype=int)

    @property
    def selected_vertices(self) -> list[Vertex]:
        return self._categories[Vertex.VertexState.SELECTED]


class QEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)

        self._state_manager = StateManager()

        # Shapes
        self._shapes: list[Shape] = []
        self._current_shape: Shape | None = None

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
            painter.setPen(self._selecting_rect_pen)
            painter.setBrush(self._selection_rect_brush)
            painter.drawRect(self._selecting_rect)
        elif self._selected_rect is not None:
            painter.setPen(self._selected_rect_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selected_rect)

    #endregion

    def mouseMoveEvent(self, event, /):
        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if self._current_shape is None: return
                position = event.position().toPoint()

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
        # temp stuff
        if event.button() == Qt.MouseButton.RightButton:
            if self._state_manager.cursor_state == StateManager.CursorState.DEFAULT:
                self._state_manager.cursor_state = StateManager.CursorState.PEN
            else:
                self._state_manager.cursor_state = StateManager.CursorState.DEFAULT
        if event.button() == Qt.MouseButton.MiddleButton:
            print(f"Cursor State: {self._state_manager.cursor_state}\nMouse State: {self._state_manager.mouse_state}"
                  f"\nAction State: {self._state_manager.action_state}\n---------------------<")
        # ----

        match self._state_manager.cursor_state:
            case StateManager.CursorState.LOCKED: return
            case StateManager.CursorState.DEFAULT:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self._current_shape is None: return
                    position = event.position().toPoint()

                    # Mouse left button is pressed
                    self._state_manager.mouse_state = StateManager.MouseState.HOLDING_MB1

                    # Mouse left button was pressed while over a vertex
                    if self._current_shape.near_vertex(position) is not None:
                        self._state_manager.action_state = StateManager.ActionState.MOVING_VERTEX
                        self._current_shape.hold_vertex(self._current_shape.near_vertex(position), unselect_others=True)

                    # Mouse left button was pressed while over a selection rectangle
                    elif self._selected_rect is not None and self._selected_rect.contains(position):
                        self._state_manager.action_state = StateManager.ActionState.MOVING_VERTICES
                        self._current_shape.hold_selection()
                        self._select_start_pos = position # Updates the position of the start of the delta (type shi)

                    # Mouse left button was pressed while floating
                    else:
                        self._state_manager.action_state = StateManager.ActionState.SELECTING_VERTICES
                        self._current_shape.reset_selected_vertices() # Unselect all currently selected vertices
                        self._selecting_rect = QRect(position, position) # The blue rectangle thing

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
                    if self._current_shape is not None: self._current_shape.release_all()
                    self._selecting_rect = None
                    self._update_selected_rect()

                    self._state_manager.mouse_state = StateManager.MouseState.DEFAULT
                    self._state_manager.action_state = StateManager.ActionState.DEFAULT

            case StateManager.CursorState.PEN:
                ...

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
        self._current_shape.close_path()
        self._current_shape = None

        self._state_manager.action_state = StateManager.ActionState.DEFAULT
        self._state_manager.mouse_state = StateManager.MouseState.DEFAULT
        self._state_manager.cursor_state = StateManager.CursorState.DEFAULT

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QEditor()
    demo.show()
    sys.exit(app.exec())