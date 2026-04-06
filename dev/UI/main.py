import os
import sys
import ressources_rc

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QPalette, QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout

from dev.moteur_physiques.vector_obstacle import VectorObstacle
from q_state_manager import QStateManager
from q_editor import QEditor
from q_tool_bar import QToolBar


class Main(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._initial_res = 1080
        self.resize(int((16/9)*self._initial_res), self._initial_res)

        QFontDatabase.addApplicationFont(":/res/Author-Regular.ttf")
        QFontDatabase.addApplicationFont(":/res/Author-Bold.ttf")

        self._editor: QEditor
        self._state_manager = QStateManager(self)
        self.__initialize_canvas()

        self._primary_layout = QVBoxLayout(self)
        self._primary_layout.addWidget(self._editor)

    def __initialize_canvas(self):
        # Editor Setup
        self._editor = QEditor(self._state_manager)
        self._editor.switch_cursor(QStateManager.CursorState.DEFAULT)

        # Tool Bar Setup
        self._tool_bar = QToolBar(self._state_manager)

        # Vector Obstacle Setup
        self._vector_obstacle = VectorObstacle(self._initial_res)

        # Layout Setup
        self._lower_layout = QHBoxLayout()
        self._lower_layout.addWidget(self._tool_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._secondary_layout = QVBoxLayout(self._editor)
        self._secondary_layout.addStretch()
        self._secondary_layout.addLayout(self._lower_layout)

        # Signals
        # State Manager
        self._state_manager.cursorStateChanged.connect(self._editor.switch_cursor)
        self._state_manager.cursorStateChanged.connect(self._tool_bar.update_cursor_state)

        # Editor
        self._editor.vectorDrawingChanged.connect(self._vector_obstacle.set_vertices)

        # Settings (General)
        self._tool_bar.settings.general_tab.resolution.realValueChanged.connect(
            self._vector_obstacle.set_reduction_factor)

    def keyPressEvent(self, event):
        self._editor.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._editor.keyReleaseEvent(event)

    # def resizeEvent(self, event):
    #     self._tool_bar.settings.general_tab.resolution.maximum = self.width()

class ThemeManager:
    def __init__(self, q_app: QApplication):
        self._q_app = q_app

        self._load_styles()
        self._palette: QPalette | None = None
        self._apply_dark_palette()

    def _apply_dark_palette(self) -> None:
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#F5F5F5"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#1D1D1D64"))
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#1D1D1D"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1D1D1D"))

        self._q_app.setPalette(dark_palette)

        self._palette = dark_palette

        self._inherit_palette(self._q_app)

    def _inherit_palette(self, q_widget: QWidget | QApplication):
        for child in q_widget.findChildren(QWidget):
            child.setPalette(self._palette)
            self._inherit_palette(child)

    def _load_styles(self) -> None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        styles_path = os.path.join(base_path, "styles.qss")

        if os.path.exists(styles_path):
            with open(styles_path, "r") as file:
                self._q_app.setStyleSheet(file.read())

        else:
            print("'styles.qss' file was not found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ThemeManager(app)
    main = Main()
    main.show()
    sys.exit(app.exec())