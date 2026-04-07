import sys

from PySide6.QtCore import QSize, Slot, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QApplication

from q_state_manager import QStateManager
from q_settings_tab import QSettingsTab

class QToolPB(QPushButton):
    def __init__(self, icon: QIcon, checkable: bool = True, parent: QWidget | None = None):
        super().__init__(parent)

        self.setIcon(icon)
        self.setIconSize(QSize(21, 21))
        self.setFixedSize(44, 44)
        self.setCheckable(checkable)
        self.setProperty("class", "tool_pb")

class QToolBar(QWidget):
    def __init__(self, state_manager: QStateManager, parent: QWidget | None = None):
        super().__init__(parent)

        self._cursor_state = QStateManager.CursorState.DEFAULT
        self._state_manager = state_manager

        # setup
        primary_frame = QFrame()
        primary_frame.setProperty("class", "primary_frame")
        primary_frame.setFixedHeight(56)
        primary_frame.setFixedWidth(255)
        primary_layout = QHBoxLayout(primary_frame)
        primary_layout.setContentsMargins(5, 5, 5, 5)

        # default button
        default_icon = QIcon(":/res/cursor_icon_black.png")
        self._default_button = QToolPB(default_icon)
        self._default_button.setChecked(True)

        # pen button
        pen_icon = QIcon(":/res/pen_icon_black.png")
        self._pen_button = QToolPB(pen_icon)

        # play button
        self._play_icon = QIcon(":/res/play_icon_black.png")
        self._stop_icon = QIcon(":/res/stop_icon_black.png")
        self._play_button = QPushButton()
        self._play_button.setCheckable(True)
        self._play_button.setProperty("class", "play_pb")
        self._play_button.setIcon(self._play_icon)
        self._play_button.setIconSize(QSize(21, 21))
        self._play_button.setFixedSize(44, 44)

        # optimize button
        optimize_icon = QIcon(":/res/optimize_icon_black.png")
        optimize_button = QToolPB(optimize_icon, checkable=False)

        # pause button
        self._pause_icon = QIcon(":/res/pause_icon_black.png")
        self._pause_button = QPushButton()
        self._pause_button.setCheckable(True)
        self._pause_button.setVisible(False)
        self._pause_button.setProperty("class", "pause_pb")
        self._pause_button.setIcon(self._pause_icon)
        self._pause_button.setIconSize(QSize(21, 21))
        self._pause_button.setFixedSize(44, 44)

        # settings
        settings_icon = QIcon(":/res/settings_icon_black.png")
        self._settings_button = QToolPB(settings_icon)
        self._settings = QSettingsTab()
        self._settings.hide()

        primary_layout.addWidget(self._default_button)
        primary_layout.addWidget(self._pen_button)
        primary_layout.addWidget(self._play_button)
        primary_layout.addWidget(optimize_button)
        primary_layout.addWidget(self._settings_button)

        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(5)
        root_layout.addWidget(self._settings, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        root_layout.addWidget(self._pause_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        root_layout.addWidget(primary_frame, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(root_layout)

        # connect signals
        self._default_button.clicked.connect(self._on_cursor_button_pressed)
        self._pen_button.clicked.connect(self._on_cursor_button_pressed)
        self._settings_button.clicked.connect(self._on_settings_button_pressed)

        self._play_button.clicked.connect(self._on_anim_button_pressed)
        self._pause_button.clicked.connect(self._on_anim_button_pressed)

    @property
    def settings(self):
        return self._settings

    @Slot()
    def _on_cursor_button_pressed(self):
        sender = self.sender()
        # The default cursor was pressed
        if sender == self._default_button:
            # Cursor was already set to default
            if self._cursor_state == QStateManager.CursorState.DEFAULT:
                self._default_button.setChecked(True)
                return

            # Cursor was not set to default
            state = QStateManager.CursorState.DEFAULT
            self._default_button.setChecked(True)
            self._pen_button.setChecked(False)
        # The pen cursor was pressed
        elif sender == self._pen_button:
            # Cursor was already set to pen
            if self._cursor_state == QStateManager.CursorState.PEN:
                self._pen_button.setChecked(True)
                return

            # Cursor was not set to pen
            state = QStateManager.CursorState.PEN
            self._default_button.setChecked(False)
            self._pen_button.setChecked(True)
        else:
            return

        self._cursor_state = state
        self._state_manager.set_cursor_state(state)

    @Slot()
    def _on_anim_button_pressed(self):
        sender = self.sender()
        if sender == self._play_button:
            if self._play_button.isChecked():
                self._settings_button.setDisabled(True)
                self._settings.hide()

                self._pen_button.setDisabled(True)
                self._state_manager.set_cursor_state(QStateManager.CursorState.DEFAULT)

                self._pause_button.setChecked(False)
                self._pause_button.setVisible(True)

                self._pause_button.setIcon(self._pause_icon)
                self._play_button.setIcon(self._stop_icon)
            else:
                self._settings_button.setDisabled(False)
                self._settings_button.setChecked(False)
                self._pen_button.setDisabled(False)

                self._pause_button.setVisible(False)
                self._play_button.setIcon(self._play_icon)
        elif sender == self._pause_button:
            if self._pause_button.isChecked():
                self._pause_button.setIcon(self._play_icon)
            else:
                self._pause_button.setIcon(self._pause_icon)

    @Slot(QStateManager.CursorState)
    def update_cursor_state(self, state: QStateManager.CursorState):
        self._cursor_state = state
        self._default_button.setChecked(state == QStateManager.CursorState.DEFAULT)
        self._pen_button.setChecked(state == QStateManager.CursorState.PEN)

    @Slot()
    def _on_settings_button_pressed(self):
        if self._settings_button.isChecked():
            self._settings.show()
        else:
            self._settings.hide()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QToolBar()
    window.show()
    sys.exit(app.exec())