from dev.user_interface.tools.float_comparator import is_not_close, is_less
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QSlider
from dev.user_interface.tools.q_utils import BlockSignals


# -----------------------------------------------------------------------------
# NOTES
# -----------------------------------------------------------------------------
# THIS IS JUST A QSLIDER ADAPTATION FROM THE ORIGINAL QREALSCROLLBAR
#
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

    def _to_real_scale(self, int_value: int) -> float:
        return self._range_scale * int_value

    def _to_int_scale(self, real_value: float) -> int:
        return round(real_value / self._range_scale)

    def _to_real_value(self, int_value: int) -> float:
        return self._real_minimum + self._range_scale * int_value

    def _to_int_index(self, real_value: float) -> int:
        return round((real_value - self._real_minimum) / self._range_scale)

    def _setup(self) -> None:
        slide_value: float = self.value()

        with BlockSignals(self):
            self._precision_scale = 10 ** self._decimals
            super().setRange(0, int(round(self._precision_scale * (self._real_maximum - self._real_minimum))))

            self._range_scale = (self._real_maximum - self._real_minimum) / (
                    super().maximum() - super().minimum())

            super().setSingleStep(self._to_int_scale(self._single_step))
            super().setPageStep(self._to_int_scale(self._page_step))

            self.setValue(slide_value)

        if is_not_close(slide_value, self.value()):
            self.realValueChanged.emit(self.value())

    @Slot(int)
    def _on_value_changed(self, _: int) -> None:
        self.realValueChanged.emit(self.value())

    @Slot(int)
    def _on_slider_moved(self, _: int) -> None:
        self.realSliderMoved.emit(self.value())

    @Slot(int, int)
    def _on_range_changed(self, min: int, max: int) -> None:
        self.realRangeChanged.emit(self._real_minimum, self._real_maximum)

    def decimals(self) -> int:
        return self._decimals

    def setDecimals(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError('decimals must be an int')
        if not 0 < value <= 6:
            raise ValueError('decimals must be between 1 and 6')
        if value != self._decimals:
            self._decimals = value
            self._setup()
            self.decimalsChanged.emit(self._decimals)

    def minimum(self) -> float:
        return self._real_minimum

    def setMinimum(self, value: float | int) -> None:
        self.setRange(float(value), self._real_maximum)

    def maximum(self) -> float:
        return self._real_maximum

    def setMaximum(self, value: float | int) -> None:
        self.setRange(self._real_minimum, float(value))

    def value(self) -> float:
        return self._to_real_value(super().value())

    @Slot(float)
    def setValue(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('value must be a float or int')
        value = float(value)
        if is_not_close(value, self.value()):
            super().setValue(self._to_int_index(value))

    def singleStep(self) -> float:
        return self._single_step

    def setSingleStep(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('single_step must be a float or int')
        value = float(value)
        if is_not_close(value, self._single_step):
            self._single_step = value
            self._setup()

    def pageStep(self) -> float:
        return self._page_step

    def setPageStep(self, value: float | int) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError('page_step must be a float or int')
        value = float(value)
        if is_not_close(value, self._page_step):
            self._page_step = value
            self._setup()

    @Slot(float, float)
    def setRange(self, minimum: float | int, maximum: float | int) -> None:
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


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# INTERACTIVE TESST WIDGET
# -----------------------------------------------------------------------------
class TestWidget(QWidget):
    """An interactive widget to test all features of QRealSlider."""

    def __init__(self, parent: QWidget | None = None):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QFormLayout, QVBoxLayout, QLabel, QGroupBox, QSpinBox, QDoubleSpinBox
        )
        super().__init__(parent)
        self.setWindowTitle("QRealSlider Interactive Test")

        # --- Widgets ---
        self.real_slider = QRealSlider()
        self.real_slider.setOrientation(Qt.Orientation.Horizontal)

        self.value_label = QLabel()
        self.range_label = QLabel()

        # Controls for properties
        self.decimals_spin = QSpinBox()
        self.decimals_spin.setMinimum(1)
        self.decimals_spin.setMaximum(6)

        self.min_spin = QDoubleSpinBox()
        self.min_spin.setMinimum(-1000.0)
        self.min_spin.setMaximum(1000.0)
        self.min_spin.setDecimals(4)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setMinimum(-1000.0)
        self.max_spin.setMaximum(1000.0)
        self.max_spin.setDecimals(4)

        self.single_step_spin = QDoubleSpinBox()
        self.single_step_spin.setDecimals(4)

        self.page_step_spin = QDoubleSpinBox()
        self.page_step_spin.setDecimals(4)

        # --- Layout ---
        display_layout = QFormLayout()
        display_layout.addRow("Current Value:", self.value_label)
        display_layout.addRow("Current Range:", self.range_label)

        controls_layout = QFormLayout()
        controls_layout.addRow("Decimals:", self.decimals_spin)
        controls_layout.addRow("Minimum:", self.min_spin)
        controls_layout.addRow("Maximum:", self.max_spin)
        controls_layout.addRow("Single Step:", self.single_step_spin)
        controls_layout.addRow("Page Step:", self.page_step_spin)

        controls_group = QGroupBox("Controls")
        controls_group.setLayout(controls_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(display_layout)
        main_layout.addWidget(self.real_slider)
        main_layout.addWidget(controls_group)

        # --- Initial State & Connections ---
        self.init_control_values()
        self.connect_signals()
        self.update_all_labels()

    def init_control_values(self):
        """Initializes all control widgets with the slider's default state."""
        for widget in [self.decimals_spin, self.min_spin, self.max_spin,
                       self.single_step_spin, self.page_step_spin]:
            widget.blockSignals(True)

        self.real_slider.setRange(0.0, 10.0)
        self.real_slider.setValue(3.142)
        self.real_slider.setSingleStep(0.01)
        self.real_slider.setPageStep(1.0)
        self.real_slider.setDecimals(3)

        self.decimals_spin.setValue(self.real_slider.decimals())
        self.min_spin.setValue(self.real_slider.minimum())
        self.max_spin.setValue(self.real_slider.maximum())
        self.single_step_spin.setValue(self.real_slider.singleStep())
        self.page_step_spin.setValue(self.real_slider.pageStep())

        for widget in [self.decimals_spin, self.min_spin, self.max_spin,
                       self.single_step_spin, self.page_step_spin]:
            widget.blockSignals(False)

    def connect_signals(self):
        self.real_slider.realValueChanged.connect(self.update_value_label)
        self.real_slider.realRangeChanged.connect(self.update_all_labels)

        self.decimals_spin.valueChanged.connect(self.on_decimals_changed)
        self.min_spin.valueChanged.connect(self.on_range_control_changed)
        self.max_spin.valueChanged.connect(self.on_range_control_changed)
        self.single_step_spin.valueChanged.connect(self.on_single_step_changed)
        self.page_step_spin.valueChanged.connect(self.on_page_step_changed)

    @Slot(float)
    def update_value_label(self, value: float):
        self.value_label.setText(f"{value:.{self.real_slider.decimals()}f}")

    @Slot()
    def update_all_labels(self):
        self.update_value_label(self.real_slider.value())
        min_val, max_val = self.real_slider.minimum(), self.real_slider.maximum()
        self.range_label.setText(f"[{min_val}, {max_val}]")
        self.single_step_spin.setValue(self.real_slider.singleStep())
        self.page_step_spin.setValue(self.real_slider.pageStep())

    @Slot(int)
    def on_decimals_changed(self, value: int):
        self.real_slider.setDecimals(value)
        self.update_all_labels()

    @Slot(float)
    def on_range_control_changed(self, value: float):
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        if is_less(min_val, max_val):
            self.real_slider.setRange(min_val, max_val)
        else:
            print(f"Warning: Invalid range ignored (min={min_val}, max={max_val})")

    @Slot(float)
    def on_single_step_changed(self, value: float):
        try:
            self.real_slider.setSingleStep(value)
        except ValueError as e:
            print(f"Warning: {e}")

    @Slot(float)
    def on_page_step_changed(self, value: float):
        try:
            self.real_slider.setPageStep(value)
        except ValueError as e:
            print(f"Warning: {e}")


def main() -> None:
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    test_widget = TestWidget()
    test_widget.resize(450, 250)
    test_widget.show()
    sys.exit(app.exec())

# Notes:
# - [1] The `# type: ignore[no-redef]` comments are used to suppress mypy
#       warnings about method redefinition when overriding properties. This
#       is a known limitation in mypy's handling of properties in subclasses.
#
#       In this case, MyPy generate a false positive, as @Property is not
#       recognized but should be.
#
# - [2] The `# type: ignore[method-assign]` comments are used to suppress mypy
#       warnings about assigning to properties that are defined with the
#       @Property decorator. This is necessary because mypy does not
#       recognize the dynamic nature of these properties and assumes
#       they are regular attributes.
#
#       In this case, MyPy generate a false positive, as @Property is not
#       recognized but should be.