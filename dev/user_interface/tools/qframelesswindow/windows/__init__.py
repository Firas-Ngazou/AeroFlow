# coding:utf-8
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG

import win32con
import win32gui
import win32api

import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtCore import Qt, QSize, QRect, QEvent
from PySide6.QtGui import QCloseEvent, QCursor
from PySide6.QtWidgets import QApplication, QDialog, QWidget, QMainWindow

from ..titlebar import TitleBar
from ..utils import win32_utils as win_utils
from ..utils.win32_utils import Taskbar, isSystemBorderAccentEnabled, getSystemAccentColor, QT_VERSION
from .c_structures import LPNCCALCSIZE_PARAMS
from .window_effect import WindowsWindowEffect


class WindowsFramelessWindowBase:
    """ Frameless window base class for Windows system """

    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._isSystemButtonVisible = False

    def _initFrameless(self):
        self.windowEffect = WindowsWindowEffect(self)
        self.titleBar = TitleBar(self)
        self._isResizeEnabled = True

        self.update_frameless()

        # solve issue #5
        self.window_handle().screenChanged.connect(self.__onScreenChanged)

        self.resize(500, 500)
        self.titleBar.raise_()

    def update_frameless(self):
        """ update frameless window """
        stayOnTop = Qt.WindowType.WindowStaysOnTopHint if self.window_flags() & Qt.WindowType.WindowStaysOnTopHint else 0
        self.set_window_flags(self.window_flags() | Qt.WindowType.FramelessWindowHint | stayOnTop)

        # add DWM shadow and window animation
        self.windowEffect.addWindowAnimation(self.win_id())
        if not isinstance(self, AcrylicWindow):
            self.windowEffect.addShadowEffect(self.win_id())

    def refresh_background_blur_effect(self):
        """ Refresh background blur effect """
        self.windowEffect.disableBlurBehindWindow(self.win_id())
        self.windowEffect.removeWindowAnimation(self.win_id())
        self.windowEffect.enableBlurBehindWindow(self.win_id())
        self.windowEffect.addWindowAnimation(self.win_id())

    def set_title_bar(self, titleBar):
        """ set custom title bar

        Parameters
        ----------
        titleBar: TitleBar
            title bar
        """
        self.titleBar.delete_later()
        self.titleBar.hide()
        self.titleBar = titleBar
        self.titleBar.set_parent(self)
        self.titleBar.raise_()

    def set_resize_enabled(self, isEnabled: bool):
        """ set whether resizing is enabled """
        self._isResizeEnabled = isEnabled

    def set_stay_on_top(self, isTop: bool):
        """ set the stay on top status """
        if isTop:
            self.set_window_flags(self.window_flags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.set_window_flags(self.window_flags() & ~Qt.WindowType.WindowStaysOnTopHint)

        self.update_frameless()
        self.show()

    def toggle_stay_on_top(self):
        """ toggle the stay on top status """
        if self.window_flags() & Qt.WindowType.WindowStaysOnTopHint:
            self.set_stay_on_top(False)
        else:
            self.set_stay_on_top(True)

    def is_system_button_visible(self):
        """ Returns whether the system title bar button is visible """
        return self._isSystemButtonVisible

    def set_system_title_bar_button_visible(self, isVisible):
        """ set the visibility of system title bar button, only works for macOS """
        pass

    def system_title_bar_rect(self, size: QSize) -> QRect:
        """ Returns the system title bar rect, only works for macOS

        Parameters
        ----------
        size: QSize
            original system title bar rect
        """
        return QRect(0, 0, size.width(), size.height())

    def native_event(self, event_type, message):
        """ Handle the Windows message """
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return False, 0

        if msg.message == win32con.WM_NCHITTEST and self._isResizeEnabled:
            xPos, yPos = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos())
            clientRect = win32gui.GetClientRect(msg.hWnd)

            w = clientRect[2] - clientRect[0]
            h = clientRect[3] - clientRect[1]

            # fixes https://github.com/zhiyiYo/PyQt-Frameless-Window/issues/98
            bw = 0 if win_utils.isMaximized(msg.hWnd) or win_utils.isFullScreen(msg.hWnd) else self.BORDER_WIDTH
            lx = xPos < bw  # left
            rx = xPos > w - bw  # right
            ty = yPos < bw  # top
            by = yPos > h - bw  # bottom
            if lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif ty:
                return True, win32con.HTTOP
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif rx:
                return True, win32con.HTRIGHT
        elif msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            isMax = win_utils.isMaximized(msg.hWnd)
            isFull = win_utils.isFullScreen(msg.hWnd)

            # adjust the size of client rect
            if isMax and not isFull:
                ty = win_utils.getResizeBorderThickness(msg.hWnd, False)
                rect.top += ty
                rect.bottom -= ty

                tx = win_utils.getResizeBorderThickness(msg.hWnd, True)
                rect.left += tx
                rect.right -= tx

            # handle the situation that an auto-hide taskbar is enabled
            if (isMax or isFull) and Taskbar.isAutoHide():
                position = Taskbar.getPosition(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            result = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, result
        elif msg.message == win32con.WM_SETFOCUS and isSystemBorderAccentEnabled():
            self.windowEffect.setBorderAccentColor(self.win_id(), getSystemAccentColor())
        elif msg.message == win32con.WM_KILLFOCUS and isSystemBorderAccentEnabled():
            self.windowEffect.removeBorderAccentColor(self.win_id())

        return False, 0

    def __onScreenChanged(self):
        hWnd = int(self.window_handle().win_id())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    def resize_event(self, e):
        self.titleBar.resize(self.width, self.titleBar.height)


class WindowsFramelessWindow(WindowsFramelessWindowBase, QWidget):
    """  Frameless window for Windows system """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._initFrameless()


class AcrylicWindow(WindowsFramelessWindow):
    """ A frameless window with acrylic effect """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__closedByKey = False

    def _initFrameless(self):
        super()._initFrameless()
        self.update_frameless()

        self.style_sheet = "AcrylicWindow{background:transparent}"

    def update_frameless(self):
        stayOnTop = Qt.WindowType.WindowStaysOnTopHint if self.window_flags() & Qt.WindowType.WindowStaysOnTopHint else 0
        if QT_VERSION < (6, 10, 0):
            self.set_window_flags(Qt.WindowType.FramelessWindowHint | stayOnTop)
        else:
            # fix issue #206
            self.set_window_flags(Qt.WindowType.Window | Qt.WindowType.NoTitleBarBackgroundHint | stayOnTop)

        self.windowEffect.enableBlurBehindWindow(self.win_id())
        self.windowEffect.addWindowAnimation(self.win_id())

        self.windowEffect.setAcrylicEffect(self.win_id())
        if win_utils.isGreaterEqualWin11():
            self.windowEffect.addShadowEffect(self.win_id())

    def native_event(self, event_type, message):
        """ Handle the Windows message """
        msg = MSG.from_address(int(message))

        # handle Alt+F4
        if msg.message == win32con.WM_SYSKEYDOWN:
            if msg.wParam == win32con.VK_F4:
                self.__closedByKey = True
                QApplication.sendEvent(self, QCloseEvent())
                return False, 0

        return super().native_event(event_type, message)

    def event(self, e: QEvent):
        if e.type() == QEvent.Type.WindowStateChange:
            if win_utils.isMaximized(self.win_id()):
                self.refresh_background_blur_effect()

        return super().event(e)

    def close_event(self, e):
        if not self.__closedByKey or QApplication.quitOnLastWindowClosed():
            self.__closedByKey = False
            return super().close_event(e)

        # system tray icon
        self.__closedByKey = False
        self.hide()


class WindowsFramelessMainWindow(WindowsFramelessWindowBase, QMainWindow):
    """ Frameless main window for Windows system """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._initFrameless()


class WindowsFramelessDialog(WindowsFramelessWindowBase, QDialog):
    """ Frameless dialog for Windows system """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._initFrameless()
        self.titleBar.minBtn.hide()
        self.titleBar.maxBtn.hide()
        self.titleBar.set_double_click_enabled(False)
        self.windowEffect.disableMaximizeButton(self.win_id())

