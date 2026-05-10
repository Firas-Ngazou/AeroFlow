from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout

from dev.user_interface.components.q_buttons import QSpecialSettingPB


class QSaveClear(QWidget):
    saveRequested = Signal()
    clearRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        font = QFont("JetBrains Mono", 12)

        # Buttons
        self._save_button = QSpecialSettingPB("SAVE ( - )", False)
        self._clear_button = QSpecialSettingPB("CLEAR ( - )", False)
        self._save_button.setFont(font)
        self._clear_button.setFont(font)
        self._save_button.setDisabled(True)
        self._clear_button.setDisabled(True)
        self._save_button.height = 30
        self._clear_button.height = 30
        self._save_button.width = 160
        self._clear_button.width = 160

        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.addWidget(self._save_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._clear_button, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Connections
        self._save_button.pressed.connect(self.saveRequested.emit)
        self._clear_button.pressed.connect(self.clearRequested.emit)

    @property
    def clear_disabled(self):
        return
    @clear_disabled.setter
    def clear_disabled(self, disabled: bool):
        self._clear_button.setDisabled(disabled)

    @property
    def save_disabled(self):
        return
    @save_disabled.setter
    def save_disabled(self, disabled: bool):
        self._save_button.setDisabled(disabled)

    @property
    def save_info(self):
        return self._save_button.text
    @save_info.setter
    def save_info(self, info: str):
        self._save_button.text = f"SAVE ({info})"

    @property
    def clear_info(self):
        return self._clear_button.text
    @clear_info.setter
    def clear_info(self, info: str):
        self._clear_button.text = f"CLEAR ({info})"
