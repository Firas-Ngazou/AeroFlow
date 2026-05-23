import math
import random

import numpy as np
from PySide6.QtCore import QPoint
from PySide6.QtGui import QPen, QColor, QBrush, QFont, QPainterPath, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from vpython import graph


class QGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Texts
        self._x_text = " _ "
        self._y_text = " - "

        # Labels
        font = QFont("JetBrains Mono", 7)
        font.setBold(True)

        self._x_label = QLabel(self._x_text)
        self._y_label = QLabel(self._y_text)

        self._x_label.setFont(font)
        self._y_label.setFont(font)

        # Pens & brushes
        self._line_pen = QPen(QColor(255, 142, 142, 255))
        self._grad_pen = QPen(QColor(245, 245, 245, 255))
        self._axis_pen = QPen(QColor(245, 245, 245, 255))
        self._axis_pen.setWidth(2)

        # Axis setup
        self._x_fixed = False
        self._y_fixed = False

        self._x_max_count = 10
        self._y_max_count = 10
        self._maximize_count = False

        self._points = np.array([], dtype=object)
        self._x_range = np.array([], dtype=int)
        self._y_range = np.array([], dtype=int)

        # Global positions & scales
        self._height = 300
        self._width = 600
        self._offset = 50
        self._text_size = 7

        self._x_axis_len = self._width - self._offset
        self._y_axis_len = -self._height + self._offset

        self._point_0 = QPoint(50, self._height - self._offset)

        self._arrow_height = 10
        self._arrow_width = 6

        self._grad_len = 5
        self._grad_offset = 8

        # Cache
        self._cached_axis: QPainterPath | None = None
        self._cached_grads: QPixmap | None = None

    def paintEvent(self, event, /):
        """
        Handles the Paint Event to render visual elements on the widget.

        The method uses a QPainter to draw visual elements such as axis and gradients
        on the widget's canvas. Cached data is utilized for optimal performance, and
        the cache is updated if found invalid. - Generated using OpenAI's GPT-5.5

        :param event: The paint event containing details about the region to be
                      updated.
        :type event: QPaintEvent
        :return: None
        """
        painter = QPainter(self)

        painter.setPen(self._axis_pen)

        # Temp
        if self._cached_axis is None:
            self._update_axis_cache()

        if self._cached_axis:
            painter.drawPath(self._cached_axis)

        if self._cached_grads is None:
            self._update_grads_cache()

        if self._cached_grads:
            painter.drawPixmap(0, 0, self._cached_grads)

    def _update_axis_cache(self):
        """
        Updates the cached axis representation by modifying the `_cached_axis` attribute. This method recalculates
        and redraws the axis lines and arrowheads for both x and y axes based on current axis configurations.

        The method constructs the axes starting from a defined starting point and extends them to endpoints determined
        by the configured axis lengths. Arrowhead lines are also added to visually represent the axis directions.
        - Generated using OpenAI's GPT-5.5

        :raises AttributeError: If any required attributes (e.g., `_point_0`, `_x_axis_len`, `_y_axis_len`) are missing
            or improperly initialized.
        """
        self._cached_axis = QPainterPath()

        x_end = self._point_0 + QPoint(self._x_axis_len, 0)
        y_end = self._point_0 + QPoint(0, self._y_axis_len)

        self._cached_axis.moveTo(self._point_0)
        self._cached_axis.lineTo(x_end)

        arrow_top = x_end - QPoint(self._arrow_width, self._arrow_height//2)
        arrow_bottom = x_end - QPoint(self._arrow_width, -(self._arrow_height//2))

        self._cached_axis.moveTo(arrow_top)
        self._cached_axis.lineTo(x_end)
        self._cached_axis.moveTo(arrow_bottom)
        self._cached_axis.lineTo(x_end)

        self._cached_axis.moveTo(self._point_0)
        self._cached_axis.lineTo(y_end)

        arrow_top = y_end + QPoint(-self._arrow_height//2, self._arrow_width)
        arrow_bottom = y_end + QPoint(self._arrow_height//2, self._arrow_width)

        self._cached_axis.moveTo(arrow_top)
        self._cached_axis.lineTo(y_end)
        self._cached_axis.moveTo(arrow_bottom)
        self._cached_axis.lineTo(y_end)

    def _update_grads_cache(self):
        """
        Updates the cached gradient pixmap for rendering grid lines on a given axis.

        This function recalculates and updates the visual representation of gradient lines
        that represent the grid structure based on the current configuration of the axis.
        It creates lines at calculated intervals along the X and Y axes, taking into account
        the specified grid parameters and maximizing the number of lines or limiting them
        to a maximum count as configured. - Generated using OpenAI's GPT-5.5

        :param self: Instance of the class calling this method.

        :param self._grad_pen: The pen used for drawing gradient lines.
        :param self._width: The width of the pixmap to be updated.
        :param self._height: The height of the pixmap to be updated.
        :param self._point_0: Starting point of the gradient lines.
        :param self._x_range: Range of points for the X-axis grid computation.
        :param self._y_range: Range of points for the Y-axis grid computation.
        :param self._x_max_count: Maximum grid count allowed along the X-axis.
        :param self._y_max_count: Maximum grid count allowed along the Y-axis.
        :param self._maximize_count: Flag indicating whether to maximize grid lines or
                                      limit them to the max count set by `_x_max_count`
                                      and `_y_max_count`.
        :param self._x_axis_len: Total length of the X-axis for spacing grid lines.
        :param self._y_axis_len: Total length of the Y-axis for spacing grid lines.
        :param self._grad_len: Length of individual gradient lines for drawing grid segments.

        :return: None
        """
        self._cached_grads = QPixmap(self._width, self._height)
        self._cached_grads.fill(QColor(0, 0, 0, 0))

        painter = QPainter(self._cached_grads)

        painter.setPen(self._grad_pen)
        # painter.drawLine(start, start + QPoint(0, self._grad_len))

        x_values = self._x_range
        y_values = self._y_range

        x_given_count = len(x_values)
        y_given_count = len(y_values)

        if self._maximize_count:
            x_count = x_given_count
            y_count = y_given_count
        else:
            x_count = min(x_given_count, self._x_max_count)
            y_count = min(y_given_count, self._y_max_count)

        x_start = QPoint(self._point_0)
        y_start = QPoint(self._point_0)

        x_space = self._x_axis_len // x_count if x_count > 0 else 0
        y_space = self._y_axis_len // y_count if y_count > 0 else 0
        i_x_space = len(x_values) // x_count if x_count > 0 else 0
        i_y_space = len(y_values) // y_count if y_count > 0 else 0

        point_count = len(self._points)

        for i in range(point_count):
            if x_count > 0 and i < x_count - 1:
                x_start += QPoint(x_space, 0)
                grad_end = x_start + QPoint(0, self._grad_len)
                painter.drawLine(x_start, grad_end)

                value = x_values[i * i_x_space]
                text = str(value)
                text_start = grad_end + QPoint(0, self._grad_offset)
                text_end = ((text_start - QPoint(self._text_size // 2 + ((len(text) - 1) * self._text_size // 2), 0)) +
                            QPoint(0, self._text_size))

                painter.drawText(text_end, text)

            if y_count > 0 and i < y_count - 1:
                y_start += QPoint(0, y_space)
                grad_end = y_start - QPoint(self._grad_len, 0)
                painter.drawLine(y_start, grad_end)

                value = y_values[i * i_y_space]
                text = str(value)
                text_start = grad_end - QPoint(self._grad_offset, 0)
                text_end = ((text_start - QPoint(self._text_size // 2 + ((len(text) - 1) * self._text_size), 0)) +
                            QPoint(0, self._text_size))

                painter.drawText(text_end, text)

            if i != 0:
                current_pos = self._point_to_graph_pos(self._points[i])
                last_pos = self._point_to_graph_pos(self._points[i - 1])
                painter.drawLine(last_pos, current_pos)

        painter.end()

    def _point_to_graph_pos(self, point: QPoint):
        x_min = min(self._x_range)
        x_max = max(self._x_range)
        x_range = x_max - x_min

        y_min = min(self._y_range)
        y_max = max(self._y_range)
        y_range = y_max - y_min

        if x_range == 0 or y_range == 0:
            return QPoint(self._point_0)

        normalized_x = (point.x() - x_min) / x_range
        normalized_y = (point.y() - y_min) / y_range

        graph_x = self._point_0.x() + normalized_x * self._x_axis_len
        graph_y = self._point_0.y() - normalized_y * abs(self._y_axis_len)

        return QPoint(int(graph_x), int(graph_y))

    def add_point(self, point: QPoint):
        self._points = np.array(sorted(np.append(self._points, point), key=lambda p: p.x()), dtype=object)

        self._x_range = np.array([p.x() for p in sorted(self._points, key=lambda p: p.x())], dtype=int)
        self._y_range = np.array([p.y() for p in sorted(self._points, key=lambda p: p.y())], dtype=int)

        self.update()

if __name__ == "__main__":
    app = QApplication()
    w = QGraph()

    count = 100
    for _ in range(count):
        w.add_point(QPoint(random.randint(0, w.width()), random.randint(0, w.height())))

    w.show()
    app.exec()