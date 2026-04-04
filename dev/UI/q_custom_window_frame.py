import sys
import os
import ressources_rc

from PySide6.QtGui import QIcon, QFont, QAction, QPalette, QColor, QFontDatabase
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMenu, QHBoxLayout, \
    QFrame
from PySide6.QtCore import Qt

from qframelesswindow import FramelessWindow, TitleBar
from q_custom_widgets import QAnalysisTabPB, QHistoryGroup, QVSeperator

class QSettingsMenu(QMenu):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        new_action = QAction("Nouveau", self)
        open_action = QAction("Ouvrir", self)
        save_action = QAction("Enregistrer (CTRL + S)", self)
        save_as_action = QAction("Enregistrer sous (CTRL + SHIFT + S)", self)

        # Add actions
        self.addAction(new_action)
        self.addAction(open_action)
        self.addSeparator()
        self.addAction(save_action)
        self.addAction(save_as_action)

        # Connect actions
        new_action.triggered.connect(self._make_new_file)
        open_action.triggered.connect(self._open_file)
        save_action.triggered.connect(self._save_file)
        save_as_action.triggered.connect(self._save_file_as)

    def _make_new_file(self):
        ...

    def _open_file(self):
        ...

    def _save_file(self):
        ...

    def _save_file_as(self):
        ...

class QEditMenu(QMenu):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        rename_action = QAction("Renommer", self)
        undo_action = QAction("Annuler (CTRL + Z)", self)
        redo_action = QAction("Rétablir (CTRL + SHIFT + Z)", self)
        select_all_action = QAction("Tout sélectionner (CTRL + A)", self)
        delete_action = QAction("Supprimer (DEL/BACKSPACE)", self)

        # Add actions
        self.addAction(rename_action)
        self.addSeparator()
        self.addAction(undo_action)
        self.addAction(redo_action)
        self.addAction(select_all_action)
        self.addAction(delete_action)

        # Connect actions
        rename_action.triggered.connect(self._rename_file)
        undo_action.triggered.connect(self._undo)
        redo_action.triggered.connect(self._redo)
        select_all_action.triggered.connect(self._select_all)
        delete_action.triggered.connect(self._delete)

    def _rename_file(self):
        ...

    def _undo(self):
        ...

    def _redo(self):
        ...

    def _select_all(self):
        ...

    def _delete(self):
        ...

class QTitleBarSettingsPB(QPushButton):
    def __init__(self, text: str, menu: QMenu, parent: QWidget | None = None):
        super().__init__(parent)
        self.setText(text)
        self.setFont(QFont("JetBrains Mono", 12))
        self.setProperty("class", "titlebar_settings_pb")
        self.setFixedSize(80, 32)

        self.setMenu(menu)

class QCustomTitleBar(TitleBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setFixedHeight(32)

        # Min/max/close buttons colors
        self.minBtn.setNormalColor(QColor("#F5F5F5"))
        self.maxBtn.setNormalColor(QColor("#F5F5F5"))
        self.closeBtn.setNormalColor(QColor("#F5F5F5"))

        self.minBtn.setHoverColor(QColor("#F5F5F5"))
        self.maxBtn.setHoverColor(QColor("#F5F5F5"))

        self.minBtn.setPressedColor(QColor("#F5F5F5"))
        self.maxBtn.setPressedColor(QColor("#F5F5F5"))

        # Application icon
        self._icon_label = QLabel()

        # File settings & edit settings
        self._settings_menu = QSettingsMenu(self)
        self._edit_menu = QEditMenu(self)
        self._file_settings_pb = QTitleBarSettingsPB("Fichier", self._settings_menu)
        self._edit_settings_pb = QTitleBarSettingsPB("Édition", self._edit_menu)

        # File name
        self._file_name = QLabel()
        self._file_name.setFixedSize(170, 32)
        self._file_name.setFont(QFont("JetBrains Mono", 12))
        self._file_name.setText("*Nouveau_fichier")
        self._file_name.setStyleSheet("QLabel { color: rgba(245, 245, 245, 100); }")

        # Analysis button
        self._analysis_button = QAnalysisTabPB("Analyse")

        # History group
        self._history_group = QHistoryGroup()

        # Layout
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self._icon_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(2, 10)
        self.hBoxLayout.insertWidget(3, self._file_name, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(4, 10)
        self.hBoxLayout.insertWidget(5, QVSeperator(), 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(6, 10)
        self.hBoxLayout.insertWidget(7, self._file_settings_pb, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(8, 10)
        self.hBoxLayout.insertWidget(9, self._edit_settings_pb, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(10, 10)
        self.hBoxLayout.insertWidget(11, QVSeperator(), 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(12, 10)
        self.hBoxLayout.insertWidget(13, self._analysis_button, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.insertSpacing(14, 10)
        self.hBoxLayout.insertWidget(15, self._history_group, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.hBoxLayout.insertSpacing(16, 10)

    @property
    def icon(self):
        return
    @icon.setter
    def icon(self, icon: QIcon):
        self._icon_label.setPixmap(icon.pixmap(32, 32))

class QCustomWindowFrame(FramelessWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumWidth(850)

        self._title_bar = QCustomTitleBar(self)
        self.setTitleBar(self._title_bar)

    @property
    def title_bar(self):
        return self._title_bar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QCustomWindowFrame()
    window.show()
    app.exec()