import os
import sys
import ressources_rc

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QPalette, QColor, QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout

from q_state_manager import QStateManager
from q_editor import QEditor
from q_tool_bar import QToolBar
from q_custom_window_frame import QCustomWindowFrame


class Main(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumWidth(450)
        self._editor: QEditor
        self._state_manager = QStateManager(self)
        self.__initialize_canvas()

        self._primary_layout = QVBoxLayout(self)
        self._primary_layout.setContentsMargins(0, 0, 0, 0)
        self._primary_layout.addWidget(self._editor)

    def __initialize_canvas(self):
        self._editor = QEditor(self._state_manager)

        self._secondary_layout = QVBoxLayout(self._editor)
        self._lower_layout = QHBoxLayout()
        self._secondary_layout.addStretch()
        self._secondary_layout.addLayout(self._lower_layout)
        self._tool_bar = QToolBar(self._state_manager)
        self._lower_layout.addWidget(self._tool_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._editor.switch_cursor(QStateManager.CursorState.DEFAULT)

        # Signals
        self._state_manager.cursorStateChanged.connect(self._editor.switch_cursor)
        self._state_manager.cursorStateChanged.connect(self._tool_bar.update_cursor_state)

    def keyPressEvent(self, event):
        self._editor.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._editor.keyReleaseEvent(event)


class ThemeManager:
    def __init__(self, q_app: QApplication):
        self._q_app = q_app

        self._load_custom_fonts()
        self._load_styles()
        self._palette: QPalette | None = None
        self._apply_dark_palette()

    @staticmethod
    def _load_custom_fonts():
        QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Regular.ttf")
        QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Bold.ttf")
        QFontDatabase.addApplicationFont(":/res/Author-Regular.otf")
        QFontDatabase.addApplicationFont(":/res/Author-Bold.otf")

    def _apply_dark_palette(self) -> None:
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#F5F5F5"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#1D1D1D64"))
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#1D1D1D"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1D1D1D64"))

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

    window = QCustomWindowFrame()
    window.title_bar.icon = QIcon(":/res/app_logo.png")
    window.resize(1920, 1080)

    main = Main()

    window_layout = QVBoxLayout(window)
    window_layout.setSpacing(0)
    window_layout.setContentsMargins(0, 32, 0, 0)

    window_layout.addWidget(main)

    ThemeManager(app)

    window.show()
    sys.exit(app.exec())