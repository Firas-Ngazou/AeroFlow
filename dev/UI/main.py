import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout

from q_editor import QEditor, StateManager
from q_tool_bar import QToolBar

class Main(QWidget):
    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        self.resize(1920, 1080)

        self._editor: QEditor
        self.__initialize_canvas()

        self._primary_layout = QVBoxLayout(self)
        self._primary_layout.addWidget(self._editor)

    def __initialize_canvas(self):
        self._editor = QEditor()

        self._secondary_layout = QVBoxLayout(self._editor)
        self._lower_layout = QHBoxLayout()
        self._secondary_layout.addStretch()
        self._secondary_layout.addLayout(self._lower_layout)
        self._tool_bar = QToolBar()
        self._lower_layout.addWidget(self._tool_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._editor.switch_cursor(StateManager.CursorState.DEFAULT)

    def keyPressEvent(self, event):
        self._editor.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._editor.keyReleaseEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())