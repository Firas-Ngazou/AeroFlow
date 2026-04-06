import sys
import ressources_rc

from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QApplication, QPushButton, QVBoxLayout, QDoubleSpinBox, \
    QLabel, QComboBox

from q_custom_widgets import QSettingsTabPB, QSliderGroup, QRealSliderGroup

class QSettingsGeneralTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Resolution
        self._resolution_setting = QRealSliderGroup("QUALITY")

        self._resolution_setting.minimum = 0.1
        self._resolution_setting.maximum = 1.0
        self._resolution_setting.single_step = 0.01

        high_res_warning = QLabel("        ATTENTION : Une trop haute valeur peut résulter en une \n"
                                  "        perte de performance importante.")
        high_res_warning.setFont(QFont("Author", 8))

        # Wind speed
        self._wind_speed_setting = QRealSliderGroup("VITESSE (m/s)")

        # Layouts
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self._resolution_setting)
        root_layout.addWidget(high_res_warning, alignment=Qt.AlignmentFlag.AlignTop)
        root_layout.addSpacing(20)
        root_layout.addWidget(self._wind_speed_setting)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

    @property
    def resolution(self):
        return self._resolution_setting

class QSettingsOptimizationTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Constraint method
        # Title
        self._title = QLabel("CONTRAINTE")
        self._title.setFont(QFont("Author", 11))

        # Combobox
        self._combo_box = QComboBox()
        self._combo_box.setPlaceholderText("MÉTHODE")
        self._combo_box.setProperty("class", "settings_combo_box")
        self._combo_box.setFixedSize(150, 30)
        self._combo_box.setFont(QFont("Author", 9))

        self._combo_box.addItem("DISTANCE")
        self._combo_box.addItem("SURFACE")

        # Primary frame & layout
        constraint_frame = QFrame()
        constraint_frame.setProperty("class", "constraint_frame")
        self._constraint_layout = QHBoxLayout(constraint_frame)

        self._constraint_layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignLeft)
        self._constraint_layout.addWidget(self._combo_box, alignment=Qt.AlignmentFlag.AlignRight)
        self._constraint_layout.setContentsMargins(15, 0, 0, 0)

        # Threshold
        self._threshold_setting = QSliderGroup("SEUIL (%)")

        # Iterations
        self._iterations_setting = QSliderGroup("ITÉRATIONS MAX")

        # Root
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(constraint_frame)
        root_layout.addWidget(self._threshold_setting)
        root_layout.addWidget(self._iterations_setting)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

class QSettingsTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._current_tab = 0
        primary_frame = QFrame()
        primary_frame.setProperty("class", "primary_frame")
        primary_frame.setFixedSize(395, 280)
        primary_layout = QVBoxLayout(primary_frame)
        primary_layout.setContentsMargins(10, 10, 10, 5)
        secondary_layout = QHBoxLayout()
        secondary_layout.setContentsMargins(10, 5, 10, 5)
        primary_layout.addLayout(secondary_layout)

        # General tab
        self._general_button = QSettingsTabPB("GÉNÉRAL")
        self._general_button.setChecked(True)
        secondary_layout.addWidget(self._general_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                   Qt.AlignmentFlag.AlignLeft)
        self._general_tab = QSettingsGeneralTab()
        primary_layout.addWidget(self._general_tab)

        # Optimization tab
        self._optimization_button = QSettingsTabPB("OPTIMIZATION")
        secondary_layout.addWidget(self._optimization_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                        Qt.AlignmentFlag.AlignRight)
        self._optimization_tab = QSettingsOptimizationTab()
        primary_layout.addWidget(self._optimization_tab)
        self._optimization_tab.hide()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(primary_frame)

        # Connections
        self._general_button.clicked.connect(self._on_tab_changed)
        self._optimization_button.clicked.connect(self._on_tab_changed)

    @property
    def general_tab(self):
        return self._general_tab

    @property
    def optimization_tab(self):
        return self._optimization_tab

    @Slot()
    def _on_tab_changed(self):
        sender = self.sender()

        # General tab was pressed
        if sender == self._general_button:

            # General tab was already pressed
            if self._current_tab == 0:
                self._general_button.setChecked(True)
                return

            # General tab was not pressed
            self._general_button.setChecked(True)
            self._optimization_button.setChecked(False)
            self._current_tab = 0
            self._optimization_tab.hide()
            self._general_tab.show()

        # Optimization tab was pressed
        else:

            # Optimization tab was already pressed
            if self._current_tab == 1:
                self._optimization_button.setChecked(True)

            # Optimization tab was not pressed
            self._optimization_button.setChecked(True)
            self._general_button.setChecked(False)
            self._current_tab = 1
            self._general_tab.hide()
            self._optimization_tab.show()


def load_styles(q_app: QApplication) -> None:
    with open("styles.qss", "r") as file:
        q_app.setStyleSheet(file.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_styles(app)
    window = QSettingsTab()
    window.show()
    sys.exit(app.exec())