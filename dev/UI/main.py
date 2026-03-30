import sys
import ressources_rc

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout

from q_state_manager import QStateManager
from q_editor import QEditor
from q_tool_bar import QToolBar

class Main(QWidget):
    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        self.resize(1920, 1080)

        QFontDatabase.addApplicationFont("../fonts/Author-Regular.ttf")
        QFontDatabase.addApplicationFont("../fonts/Author-Bold.ttf")

        self._editor: QEditor
        self._state_manager = QStateManager(self)
        self.__initialize_canvas()

        self._primary_layout = QVBoxLayout(self)
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


def load_styles(q_app: QApplication) -> None:
    with open("styles.qss", "r") as file:
        q_app.setStyleSheet(file.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_styles(app)
    main = Main()
    main.show()
    sys.exit(app.exec())