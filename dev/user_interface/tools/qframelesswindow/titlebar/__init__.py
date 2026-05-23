# coding:utf-8
import sys
import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget

from ..utils import startSystemMove, toggleMaxState
from .title_bar_buttons import (CloseButton, MaximizeButton, MinimizeButton,
                                SvgTitleBarButton, TitleBarButton)


class TitleBarBase(QWidget):
    """ Title bar base class """

    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn = MinimizeButton(parent=self)
        self.closeBtn = CloseButton(parent=self)
        self.maxBtn = MaximizeButton(parent=self)

        self._isDoubleClickEnabled = True

        self.resize(200, 32)
        self.set_fixed_height(32)

        # connect signal to slot
        self.minBtn.clicked.connect(self.window().show_minimized)
        self.maxBtn.clicked.connect(self.__toggleMaxState)
        self.closeBtn.clicked.connect(self.window().close)

        self.window().install_event_filter(self)

    def event_filter(self, obj, e):
        if obj is self.window():
            if e.type() == QEvent.Type.WindowStateChange:
                self.maxBtn.set_max_state(self.window().is_maximized())
                return False

        return super().event_filter(obj, e)

    def mouse_double_click_event(self, event):
        """ Toggles the maximization state of the window """
        if event.button() != Qt.MouseButton.LeftButton or not self._isDoubleClickEnabled:
            return

        self.__toggleMaxState()

    def mouse_move_event(self, e):
        if sys.platform != "win32" or not self.canDrag(e.position()):
            return

        startSystemMove(self.window(), e.global_position())

    def mouse_press_event(self, e):
        if sys.platform == "win32" or not self.canDrag(e.position()):
            return

        startSystemMove(self.window(), e.global_position())

    def __toggleMaxState(self):
        """ Toggles the maximization state of the window and change icon """
        toggleMaxState(self.window())

    def _is_drag_region(self, pos):
        """ Check whether the position belongs to the area where dragging is allowed """
        width = 0
        for button in self.find_children(TitleBarButton):
            if button.visible:
                width += button.width

        return 0 < pos.x() < self.width - width

    def _has_button_pressed(self):
        """ whether any button is pressed """
        return any(btn.is_pressed() for btn in self.find_children(TitleBarButton))

    def canDrag(self, pos):
        """ whether the position is draggable """
        return self._is_drag_region(pos) and not self._has_button_pressed()

    def set_double_click_enabled(self, isEnabled):
        """ whether to switch window maximization status when double clicked
        Parameters
        ----------
        isEnabled: bool
            whether to enable double click
        """
        self._isDoubleClickEnabled = isEnabled



class TitleBar(TitleBarBase):
    """ Title bar """

    def __init__(self, parent):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)

        # add buttons to layout
        self.hBoxLayout.spacing = 0
        self.hBoxLayout.set_contents_margins(0, 0, 0, 0)
        self.hBoxLayout.alignment = Qt.AlignVCenter | Qt.AlignLeft
        self.hBoxLayout.add_stretch(1)
        self.hBoxLayout.add_widget(self.minBtn, 0, Qt.AlignRight)
        self.hBoxLayout.add_widget(self.maxBtn, 0, Qt.AlignRight)
        self.hBoxLayout.add_widget(self.closeBtn, 0, Qt.AlignRight)


class StandardTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.set_fixed_size(20, 20)
        self.hBoxLayout.insert_spacing(0, 10)
        self.hBoxLayout.insert_widget(1, self.iconLabel, 0, Qt.AlignLeft)
        self.window().windowIconChanged.connect(self.set_icon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insert_widget(2, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.titleLabel.style_sheet = """
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px
            }
        """
        self.window().windowTitleChanged.connect(self.set_title)

    def set_title(self, title):
        """ set the title of title bar
        Parameters
        ----------
        title: str
            the title of title bar
        """
        self.titleLabel.text = title
        self.titleLabel.adjust_size()

    def set_icon(self, icon):
        """ set the icon of title bar
        Parameters
        ----------
        icon: QIcon | QPixmap | str
            the icon of title bar
        """
        self.iconLabel.pixmap = QIcon(icon).pixmap(20, 20)