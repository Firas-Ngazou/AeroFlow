from dev.user_interface.tools.float_comparator import is_not_close, is_less

# -----------------------------------------------------------------------------
import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtCore import Signal, Slot, Property
from PySide6.QtWidgets import QWidget, QSlider

# -----------------------------------------------------------------------------
from shibokensupport import feature  # type: ignore[import-not-found]

feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------

from dev.user_interface.tools.q_utils import BlockSignals


# -----------------------------------------------------------------------------
# NOTES
# -----------------------------------------------------------------------------
# Qt's vs Python's properties
# @Property vs @property
#
# This widget uses the basic form of the Qt's @Property instead of standard
# Python `@property` decorators for its API management (value, minimum,
# decimals, etc.).
#
# This approach facilitates the integration with advanced Qt systems like QML
# or QPropertyAnimation.
# -----------------------------------------------------------------------------


class QRealSlider(QSlider):
    """A QSlider that handles float values.

    The QRealSlider class provides a slider bar handling float values. The
    appearance and behavior is practically the same as QSlider, but all
    values are real numbers instead of integers.

    The main differences with QSlider:
    1. The value, range, single_step, and page_step properties are all floats.
    2. The 'decimals' property defines the number of decimal places,
       allowing to set the float resolution (default is 2).
    3. `realValueChanged`, `realRangeChanged`, and `realSliderMoved` signals
       are emitted with float values. These are the primary signals to use.

    Be aware that the original int-based properties of QSlider are still
    used internally. While the original signals (`valueChanged(int)`,
    `rangeChanged(int)`, etc.) are still emitted, you should connect to their
    "real" counterparts for float-based logic.

    The properties are:
    - minimum     [float] : The minimum value of the slider's range.
    - maximum     [float] : The maximum value of the slider's range.
    - value       [float] : The current float value of the slider.
    - single_step [float] : The small step size for arrow clicks.
    - page_step   [float] : The large step size for page up/down clicks.
    - decimals    [int  ] : The number of decimal places used for float values (1 to 6).

    The slots are:
    - set_range(minimum: float, maximum: float)          : Sets the slider bar's range.
    - set_value(value: float)                            : Sets the current value.
    - set_single_step(step: float)                       : Sets the single step size.
    - set_page_step(step: float)                         : Sets the page step size.
    - set_decimals(decimals: int)                        : Sets the number of decimal places.
    - setup_tooltip(description: str, details: str = '') : Sets up a tooltip for the entire widget.

    The signals are:
    - realValueChanged(float)        : Emitted when the float value changes.
    - realRangeChanged(float, float) : Emitted when the float range changes.
    - realSliderMoved(float)         : Emitted when the slider is moved.
    - decimalsChanged(int)           : Emitted when the decimals property changes.

    This class is an example of inheriting and extending Qt widgets to add
    functionality while maintaining compatibility with existing Qt systems.
    Another approach could have been to create a composite widget that
    contains a QSlider, but that would have required more boilerplate code
    to forward properties and signals. Both approaches have their merits.
    This is a more advanced example even if it's not the overall best solution
    for a professional context. The better approach is to inherit from
    QAbstractSlider. Again, this is an educational example.
    """

    realRangeChanged = Signal(float, float)
    realSliderMoved = Signal(float)
    realValueChanged = Signal(float)
    decimalsChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._real_minimum: float = 0.0
        self._real_maximum: float = 1.0
        self._single_step: float = 0.01
        self._page_step: float = 0.1
        self._decimals: int = 2

        self._precision_scale: float = 1.0
        self._range_scale: float = 1.0

        self.valueChanged.connect(self._on_value_changed)
        self.sliderMoved.connect(self._on_slider_moved)
        self.rangeChanged.connect(self._on_range_changed)

        self._setup()

    def _set_super_property(self, name: str, value: int) -> None:
        # Since `super()` returns a proxy object, writing `super().value = ...`
        # fails. The expression `super().value` calls the parent's getter and
        # returns its result (a value), to which a new value cannot be assigned
        # as intended. The property object itself is not returned. The
        # workaround is to access the property's setter directly via `.fset()`.
        #
        # Sets a property on the parent QSlider using the fset workaround.
        prop = getattr(super(QRealSlider, QRealSlider), name)
        prop.fset(self, value)

    def _to_real_scale(self, int_value: int) -> float:
        return self._range_scale * int_value

    def _to_int_scale(self, real_value: float) -> int:
        return round(real_value / self._range_scale)

    def _to_real_value(self, int_value: int) -> float:
        return self._real_minimum + self._range_scale * int_value

    def _to_int_index(self, real_value: float) -> int:
        return round((real_value - self._real_minimum) / self._range_scale)

    def _setup(self) -> None:  # Signals are blocked when calling this method

        slide_value: float = self.value

        with BlockSignals(self):
            self._precision_scale = 10 ** self._decimals
            super().set_range(0, int(round(self._precision_scale * (self._real_maximum - self._real_minimum))))

            self._range_scale = (self._real_maximum - self._real_minimum) / (
                        super().maximum - super().minimum)  # Since minimum < maximum, the division is safe

            self._set_super_property("single_step", self._to_int_scale(self._single_step))
            self._set_super_property("page_step", self._to_int_scale(self._page_step))

            self.value = slide_value  # type: ignore[method-assign] # notes: [2] see Notes at the end of the file

        if is_not_close(slide_value, self.value):  # if the value was changed by the modification of the range
            self.realValueChanged.emit(self.value)

    @Slot(int)
    def _on_value_changed(self, _: int) -> None:
        self.realValueChanged.emit(self.value)

    @Slot(int)
    def _on_slider_moved(self, _: int) -> None:
        self.realSliderMoved.emit(self.value)

    @Slot(int, int)
    def _on_range_changed(self, min: int, max: int) -> None:
        self.realRangeChanged.emit(self._real_minimum, self._real_maximum)

    @Property(int)
    def decimals(self) -> int:
        """The number of decimal places used for float values (1 to 6)."""
        return self._decimals

    @decimals.setter  # type: ignore[no-redef]
    def decimals(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError('decimals must be an int')
        if not 0 < value <= 6:
            raise ValueError('decimals must be between 1 and 6')
        if value != self._decimals:
            self._decimals = value
            self._setup()
            self.decimalsChanged.emit(self._decimals)

    @Property(float)
    def minimum(self) -> float:
        """The minimum value of the slider's range."""
        return self._real_minimum

    @minimum.setter  # type: ignore[no-redef] # notes: [1] see Notes at the end of the file
    def minimum(self, value: float | int) -> None:
        self.set_range(float(value), self._real_maximum)

    @Property(float)
    def maximum(self) -> float:
        """The maximum value of the slider's range."""
        return self._real_maximum

    @maximum.setter  # type: ignore[no-redef] # notes: [1] see Notes at the end of the file
    def maximum(self, value: float | int) -> None:
        self.set_range(self._real_minimum, float(value))

    @Property(float)
    def value(self) -> float:
        """The current float value of the slider."""
        return self._to_real_value(super().value)

    @value.setter  # type: ignore[no-redef] # notes: [1] see Notes at the end of the file
    def value(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('value must be a float or int')
        value = float(value)
        if is_not_close(value, self.value):
            self._set_super_property('value', self._to_int_index(value))

    @Property(float)
    def single_step(self) -> float:
        """The small step size for arrow clicks."""
        return self._single_step

    @single_step.setter  # type: ignore[no-redef] # notes: [1] see Notes at the end of the file
    def single_step(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('single_step must be a float or int')
        value = float(value)
        if is_not_close(value, self._single_step):
            self._single_step = value
            self._setup()

    @Property(float)
    def page_step(self) -> float:
        """The large step size for page up/down clicks."""
        return self._page_step

    @page_step.setter  # type: ignore[no-redef] # notes: [1] see Notes at the end of the file
    def page_step(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('page_step must be a float or int')
        value = float(value)
        if is_not_close(value, self._page_step):
            self._page_step = value
            self._setup()

    @Slot(float, float)
    def set_range(self, minimum: float | int, maximum: float | int) -> None:
        """Sets the slider's range from a float minimum to a float maximum."""
        if not isinstance(minimum, (float, int)):
            raise TypeError('minimum must be a float or int')
        if not isinstance(maximum, (float, int)):
            raise TypeError('maximum must be a float or int')
        minimum = float(minimum)
        maximum = float(maximum)
        if not is_less(minimum, maximum):
            raise ValueError('minimum must be less than maximum')
        if is_not_close(minimum, self._real_minimum) or is_not_close(maximum, self._real_maximum):
            self._real_minimum = minimum
            self._real_maximum = maximum
            self._setup()
            self.realRangeChanged.emit(self._real_minimum, self._real_maximum)

    @Slot(float)
    def set_value(self, value: float | int) -> None:
        """Sets the current value of the slider. This is a slot version of the value setter."""
        self.value = value  # type: ignore[method-assign] # notes: [2] see Notes at the end of the file