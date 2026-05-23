import math
import random

import numpy as np
from PySide6.QtCore import QPoint, Qt, QPointF, QMargins
from PySide6.QtGui import QPen, QColor, QBrush, QFont, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# NOTE: Last fully custom version is still available... I just didn't think of using PySide6 graphs from the start...
# and I'm not sure why... (using QChartView and QChart is a better way to do it imo though)


class QCustomGraph(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup
        self._chart = QChart()
        self._chart.setBackgroundVisible(False)
        self._chart.setMargins(QMargins(0, 0, 0, 0))
        self._chart.layout().setContentsMargins(0, 0, 0, 0)
        self._chart.legend().hide()
        self.setChart(self._chart)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._title = " - "

        # Series
        self._series = QLineSeries()
        self._chart.addSeries(self._series)
        self._chart.setTitle(self._title)

        # Axis
        self._axis_x = QValueAxis()
        self._axis_y = QValueAxis()

        # Font
        font = QFont("JetBrains Mono", 7)
        font.setBold(True)
        self._axis_x.setLabelsFont(font)
        self._axis_y.setLabelsFont(font)

        # Colors
        axis_pen = QPen(QColor(245, 245, 245, 255))
        axis_pen.setWidth(2)
        self._axis_x.setLinePen(axis_pen)
        self._axis_y.setLinePen(axis_pen)
        self._axis_x.setLabelsColor(QColor(245, 245, 245, 255))
        self._axis_y.setLabelsColor(QColor(245, 245, 245, 255))

        # Grid pen
        grad_pen = QPen(QColor(245, 245, 245, 255))
        self._axis_x.setGridLinePen(grad_pen)
        self._axis_y.setGridLinePen(grad_pen)

        self._chart.addAxis(self._axis_x, Qt.AlignmentFlag.AlignBottom)
        self._chart.addAxis(self._axis_y, Qt.AlignmentFlag.AlignLeft)

        self._series.attachAxis(self._axis_x)
        self._series.attachAxis(self._axis_y)

        # Line pen
        self._line_pen = QPen(QColor(255, 142, 142, 255))
        self._line_pen.setWidth(2)
        self._series.setPen(self._line_pen)

        self._points = []
        self._g_height = 300
        self._g_width = 600
        self._offset = 50

    def paintEvent(self, event):
        super().paintEvent(event)
        self.chart().resize(self.size())

    def add_point(self, point: QPointF):
        """
        Adds a new point to the internal collection, updates the corresponding series,
        and adjusts axis ranges based on the current set of points. - Generated using OpenAI's GPT-5.5

        :param point: The point to add; must be an instance of QPoint.
        :type point: QPointF
        :return: None
        """
        self._points.append(point)
        self._points.sort(key=lambda p: p.x())

        self._series.clear()
        for p in self._points:
            self._series.append(QPointF(p.x(), p.y()))

        if self._points:
            x_min = min(p.x() for p in self._points)
            x_max = max(p.x() for p in self._points)
            y_min = min(p.y() for p in self._points)
            y_max = max(p.y() for p in self._points)

            if x_min == x_max:
                self._axis_x.setRange(x_min - 1, x_max + 1)
            else:
                self._axis_x.setRange(x_min, x_max)

            if y_min == y_max:
                self._axis_y.setRange(y_min - 1, y_max + 1)
            else:
                self._axis_y.setRange(y_min, y_max)

    def reset(self):
        self._points.clear()
        self._series.clear()
        self._axis_x.setRange(0, 10)
        self._axis_y.setRange(0, 10)

    @property
    def g_height(self):
        return self._g_height
    @g_height.setter
    def g_height(self, value: int):
        self._g_height = value
        self.setFixedHeight(value)
        self._chart.resize(self.width(), value)

    @property
    def g_width(self):
        return self._g_width
    @g_width.setter
    def g_width(self, value: int):
        self._g_width = value
        self.setFixedWidth(value)
        self._chart.resize(value, self.height())

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, value: int):
        self._offset = value

    @property
    def x_axis_len(self):
        return self._g_width - self._offset
    @x_axis_len.setter
    def x_axis_len(self, value: int):
        self._g_width = value + self._offset
        self.setFixedWidth(self._g_width)
        self._chart.resize(self._g_width, self.height())

    @property
    def y_axis_len(self):
        return self._g_height + self._offset
    @y_axis_len.setter
    def y_axis_len(self, value: int):
        self._g_height = value + self._offset
        self.setFixedHeight(self._g_height)
        self._chart.resize(self.width(), self._g_height)

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value: str):
        self._title = value
        self._chart.setTitle(value)


if __name__ == "__main__":
    app = QApplication()
    w = QCustomGraph()

    count = 50
    for _ in range(count):
        w.add_point(QPointF(random.randint(0, 100), random.randint(0, 100)))

    w.show()
    app.exec()