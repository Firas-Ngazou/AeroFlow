import sys

from PySide6.QtGui import QIcon, QFont, QAction, QColor
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMenu, QFileDialog
from PySide6.QtCore import Qt, Signal, Slot

from qframelesswindow import FramelessWindow, TitleBar

from dev.user_interface.components.q_buttons import QSpecialSettingPB
from dev.user_interface.groups.q_history_group import QHistoryGroup
from dev.user_interface.components.q_seperators import QVSeperator

class QFileMenu(QMenu):
    newFileRequested = Signal()
    openFileRequested = Signal(str)
    saveFileRequested = Signal()
    saveAsFileRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._new_action = QAction("Nouveau", self)
        self._open_action = QAction("Ouvrir", self)
        self._save_action = QAction("Enregistrer (CTRL + S)", self)
        self._save_as_action = QAction("Enregistrer sous (CTRL + SHIFT + S)", self)

        # Add actions
        self.addAction(self._new_action)
        self.addAction(self._open_action)
        self.addSeparator()
        self.addAction(self._save_action)
        self.addAction(self._save_as_action)

        # Connect actions
        self._new_action.triggered.connect(self.newFileRequested.emit)
        self._open_action.triggered.connect(self._on_open_file_requested)
        self._save_action.triggered.connect(self.saveFileRequested.emit)
        self._save_as_action.triggered.connect(self.saveAsFileRequested.emit)

    @Slot()
    def _on_open_file_requested(self):
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "../../",
                                           "JSON Files (*.json);;All Files (*")
        if path: self.openFileRequested.emit(path)

    @Slot()
    def set_save_action_enabled(self, enabled: bool):
        self._save_action.setEnabled(enabled)

    @Slot()
    def set_new_action_enabled(self, enabled: bool):
        self._new_action.setEnabled(enabled)

class QEditMenu(QMenu):
    renameFileRequested = Signal()
    undoRequested = Signal()
    redoRequested = Signal()
    selectAllRequested = Signal()
    deleteRequested = Signal()

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
        rename_action.triggered.connect(self.renameFileRequested.emit)
        undo_action.triggered.connect(self.undoRequested.emit)
        redo_action.triggered.connect(self.redoRequested.emit)
        select_all_action.triggered.connect(self.selectAllRequested.emit)
        delete_action.triggered.connect(self.deleteRequested.emit)

class QViewMenu(QMenu):
    simulationChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._menu = QMenu("Simulation", self)
        self._density_action = QAction("Density", self)
        self._velocity_action = QAction("Average velocity", self)

        self._density_action.setCheckable(True)
        self._velocity_action.setCheckable(True)

        self._density_action.setChecked(True)

        # Add actions
        self._menu.addAction(self._density_action)
        self._menu.addAction(self._velocity_action)
        self.addMenu(self._menu)

        # Connect action
        self._density_action.triggered.connect(self._on_simulation_changed)
        self._velocity_action.triggered.connect(self._on_simulation_changed)

    def _on_simulation_changed(self):
        sender = self.sender()
        match sender:
            case self._density_action:
                self._density_action.setChecked(True)
                self._velocity_action.setChecked(False)
                self.simulationChanged.emit("density")
            case self._velocity_action:
                self._density_action.setChecked(False)
                self._velocity_action.setChecked(True)
                self.simulationChanged.emit("velocity")

class QTitleBarSettingsPB(QPushButton):
    def __init__(self, text: str, menu: QMenu, parent: QWidget | None = None):
        super().__init__(parent)
        self.setText(text)
        self.setFont(QFont("JetBrains Mono", 12))
        self.setProperty("class", "titlebar_settings_pb")
        self.setFixedSize(100, 32)

        self.setMenu(menu)

class QCustomTitleBar(TitleBar):
    newFileRequested = Signal()
    openFileRequested = Signal(str)
    saveFileRequested = Signal()
    saveAsFileRequested = Signal()
    renameFileRequested = Signal()
    undoRequested = Signal()
    redoRequested = Signal()
    selectAllRequested = Signal()
    deleteRequested = Signal()
    simulationChanged = Signal(str)
    analysisPressed = Signal(bool)

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

        # File settings & edit settings & view settings
        self._file_menu = QFileMenu(self)
        self._edit_menu = QEditMenu(self)
        self._view_menu = QViewMenu(self)
        self._file_settings_pb = QTitleBarSettingsPB("Fichier", self._file_menu)
        self._edit_settings_pb = QTitleBarSettingsPB("Édition", self._edit_menu)

        # File name
        self._file_name = QLabel()
        self._file_name.setFixedSize(170, 32)
        self._file_name.setFont(QFont("JetBrains Mono", 12))
        self._file_name.setText("*Nouveau_fichier")
        self._file_name.setStyleSheet("QLabel { color: rgba(245, 245, 245, 120); }")

        # Analysis button
        self._analysis_button = QSpecialSettingPB("Analyse")

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
        # self.hBoxLayout.insertWidget(11, self._view_settings_pb, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertWidget(11, QVSeperator(), 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.insertSpacing(12, 10)
        self.hBoxLayout.insertWidget(13, self._analysis_button, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.insertSpacing(14, 10)
        # self.hBoxLayout.insertWidget(15, self._history_group, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        # self.hBoxLayout.insertSpacing(16, 10)

        # Connections
        self._file_menu.newFileRequested.connect(self.newFileRequested.emit)
        self._file_menu.openFileRequested.connect(self.openFileRequested.emit)
        self._file_menu.saveFileRequested.connect(self.saveFileRequested.emit)
        self._file_menu.saveAsFileRequested.connect(self.saveAsFileRequested.emit)
        self._edit_menu.renameFileRequested.connect(self.renameFileRequested.emit)
        self._edit_menu.undoRequested.connect(self.undoRequested.emit)
        self._edit_menu.redoRequested.connect(self.redoRequested.emit)
        self._edit_menu.selectAllRequested.connect(self.selectAllRequested.emit)
        self._edit_menu.deleteRequested.connect(self.deleteRequested.emit)
        # self._view_menu.simulationChanged.connect(self.simulationChanged.emit)
        self._analysis_button.pressed.connect(lambda y: self.analysisPressed.emit(y))

    def click_analysis(self):
        self._analysis_button.click()

    @property
    def icon(self):
        return
    @icon.setter
    def icon(self, icon: QIcon):
        self._icon_label.setPixmap(icon.pixmap(32, 32))

    @property
    def is_analysis_checked(self):
        return self._analysis_button.is_checked
    @is_analysis_checked.setter
    def is_analysis_checked(self, value: bool):
        self._analysis_button.is_checked = value

    @property
    def file_name(self):
        return self._file_name.text
    @file_name.setter
    def file_name(self, new_name: str):
        self._file_name.setText(new_name)

class QCustomWindowFrame(FramelessWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumWidth(850)

        self._title_bar = QCustomTitleBar(self)
        self.setTitleBar(self._title_bar)

    @property
    def title_bar(self):
        return self._title_bar