from PySide6.QtCore import Signal, Slot, Qt

import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLineEdit, QPushButton


class QFloatingShapeMenu(QWidget):
    saveWithNameRequested = Signal(str)
    optimizeRequested = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.set_fixed_size(200, 90)

        font = QFont("JetBrains Mono", 12)

        main_layout = QVBoxLayout(self)
        main_layout.set_contents_margins(0, 0, 0, 0)

        self._frame = QFrame(self)
        self._frame.set_property("class", "primary_frame")
        main_layout.add_widget(self._frame)

        # LineEdit
        self._line_edit = QLineEdit()
        self._line_edit.placeholder_text = "Entrez un nom..."
        self._line_edit.hide()

        # Buttons
        self._save_btn = QPushButton("Sauvegarder")
        self._save_btn.set_property("class", "shape_settings_pb")
        self._cancel_btn = QPushButton("Annuler")
        self._cancel_btn.set_property("class", "shape_settings_pb")
        self._optimize_btn = QPushButton("Optimiser")
        self._optimize_btn.set_property("class", "shape_settings_pb")

        # Fonts
        self._line_edit.font = font
        self._save_btn.font = font
        self._cancel_btn.font = font
        self._optimize_btn.font = font

        # Layout
        self._layout = QVBoxLayout(self._frame)
        self._layout.add_widget(self._line_edit)
        self._layout.add_widget(self._save_btn)
        self._layout.add_widget(self._optimize_btn)
        self._layout.add_widget(self._cancel_btn)

        # Connections
        self._save_btn.clicked.connect(self._on_save_pressed)
        self._cancel_btn.clicked.connect(self._on_cancel_pressed)
        self._optimize_btn.clicked.connect(self._on_optimize_pressed)

        self._line_edit.returnPressed.connect(self._on_enter_pressed)
        self._line_edit.textChanged.connect(self._on_line_edit_text_changed)

        self._text_eligible = False

    @Slot()
    def _on_save_pressed(self):
        self._save_btn.hide()
        self._cancel_btn.hide()
        self._optimize_btn.hide()
        self._line_edit.show()
        self._line_edit.set_focus()

    @Slot()
    def _on_cancel_pressed(self):
        self.reset_state()

    @Slot()
    def _on_optimize_pressed(self):
        self.optimizeRequested.emit()
        self.reset_state()

    @Slot()
    def _on_line_edit_text_changed(self):
        self._text_eligible = bool(self._line_edit.text.strip())

    @Slot()
    def _on_enter_pressed(self):
        if self._text_eligible:
            text = self._line_edit.text
            no_space_text = text.replace(" ", "_")
            no_dots_text = no_space_text.replace(".", "-")

            self.saveWithNameRequested.emit(no_dots_text)
            self._on_cancel_pressed()

    def key_press_event(self, event, /):
        if event.key() == Qt.Key.Key_Escape:
            self._on_cancel_pressed()
            event.accept()
        elif event.key() == Qt.Key.Key_Enter:
            self._on_enter_pressed()
            event.accept()
        else:
            super().key_press_event(event)

    def reset_state(self):
        self._line_edit.clear()
        self._line_edit.hide()
        self._save_btn.show()
        self._cancel_btn.show()
        self._text_eligible = False
        self.hide()
