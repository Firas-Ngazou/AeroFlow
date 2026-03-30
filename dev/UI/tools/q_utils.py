# -----------------------------------------------------------------------------
# Begin: Set Shiboken feature flags for Pythonic API. -------------------------
import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]
# -----------------------------------------------------------------------------
# v--- begin all PySide6 imports ----------------------------------------------

from PySide6.QtCore import QObject
from PySide6.QtGui import QPaintDevice, QPainter

# ^--- end all PySide6 imports ------------------------------------------------
from shibokensupport import feature  # type: ignore[import-not-found]

feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()


# End: Shiboken API style is now locked. --------------------------------------
# -----------------------------------------------------------------------------
# v--- if needed, begin all custom PySide6 imports ----------------------------


class BlockSignals:
    """ Context manager to block/unblock Qt signals.

    This class is used with the 'with' statement to ensure that
    signals from a QObject are blocked upon entering the context
    and unblocked upon exiting.

    Usage:
    ```python
    def update_value_without_signals(widget: QWidget, value: int):
        with BlockSignals(widget):                  # < here, signals are blocked
            widget.set_value(value)
                                                    # < here, signals are unblocked
    ```
    """

    def __init__(self, obj: QObject):
        self._obj = obj

    def __enter__(self):
        self._obj.block_signals(True)

    def __exit__(self, *_exceptions_info):
        self._obj.block_signals(False)


class BlockSignalsTree:
    """ Context manager to block/unblock Qt signals for a widget tree.

    This class is used with the 'with' statement to ensure that signals from
    a QObject and all its children (and their descendants) are blocked upon
    entering the context and unblocked upon exiting.

    Usage:
    ```python
    def update_value_without_signals(widget: QWidget, value: int):
        with BlockSignalsTree(widget):              # < here, signals are blocked
            widget.set_value(value)
                                                    # < here, signals are unblocked
    ```
    """

    def __init__(self, obj: QObject):
        self._obj = obj

    def __enter__(self):
        self._all_objects = [self._obj] + self._obj.find_children(QObject)
        for obj in self._all_objects:
            obj.block_signals(True)

    def __exit__(self, *_exceptions_info):
        for obj in reversed(self._all_objects):
            try:  # Handle the case where the C++ object has been deleted
                obj.block_signals(False)
            except RuntimeError:
                pass
        del self._all_objects  # clean up references in case of object is created in a long-lived context or external to a context manager


class SavedState:
    """ Context manager for QPainter save/restore operations.

    This class is used with the 'with' statement to ensure that
    the QPainter's state is saved upon entering the context and
    restored upon exiting.

    The following are the state elements that are saved/restored:
    - Transformation <<<
    - Pen
    - Brush
    - Font
    - Opacity
    - Composition mode
    - ... (other QPainter state elements)

    Usage:
    ```python
    def draw_unit_circle(painter: QPainter):
        with SavedState(painter) as p:              # < here, painter state is saved and returned
            p.set_pen(Qt.NoPen)
            p.set_brush(QBrush(Qt.magenta))
            p.reset_transform()
            p.draw_ellipse(QPointF(0, 0), 1.0, 1.0)
                                                    # < here, painter state is restored
    ```
    """

    def __init__(self, painter: QPainter):
        self._painter = painter

    def __enter__(self):
        self._painter.save();
        return self._painter

    def __exit__(self, *_exceptions_info):
        self._painter.restore()


class PainterOn:
    """ Context manager for QPainter operations on a QPaintDevice.

    This class is used with the 'with' statement to ensure that
    the QPainter is properly begun and ended when drawing on a
    QPaintDevice.

    This class is useful for ensuring that the QPainter releases
    the device resources when done, even if an error occurs during
    the painting process.

    Usage:
    ```python
    def paint_event(self, event):
        with PainterOn(self) as painter:            # < here, the painter is created and returned
            painter.set_pen(Qt.NoPen)
            painter.set_brush(QBrush(Qt.magenta))
            painter.draw_ellipse(QPointF(0, 0), 1.0, 1.0)
                                                    # < here, ressources are released by calling painter.end()
    ```
    """

    def __init__(self, device: QPaintDevice):
        self._device = device

    def __enter__(self):
        self._painter = QPainter(self._device)
        return self._painter

    def __exit__(self, *_exceptions_info):
        self._painter.end()

