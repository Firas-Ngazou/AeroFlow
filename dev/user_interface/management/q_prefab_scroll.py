import json
import os

from PySide6.QtCore import Qt, QByteArray, Slot, Signal
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QFrame, QVBoxLayout, QLabel, QPushButton


class QShapePrefab(QFrame):
    deleteRequested = Signal(str)
    instanceRequested = Signal(str)

    def __init__(self, data: dict, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        font = QFont("JetBrains Mono", 9)
        self.setMouseTracking(True)
        self.setObjectName("shape_prefab_frame")

        self.setFixedSize(100, 100)
        self.setProperty("class", "primary_frame")
        self.setToolTip(data.get("Name", " - "))

        # Pixmap setup
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self._delete_button = QPushButton(self)
        self._delete_button.setText("Supprimer")
        self._delete_button.setFont(font)
        self._delete_button.setProperty("class", "delete_pb")
        self._delete_button.hide()

        self._cancel_button = QPushButton(self)
        self._cancel_button.setText("Annuler")
        self._cancel_button.setFont(font)
        self._cancel_button.setProperty("class", "shape_settings_pb")
        self._cancel_button.hide()

        self._settings_visible = False

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self._image_label)
        layout.addWidget(self._delete_button)
        layout.addWidget(self._cancel_button)

        # Make pixmap
        self._name = data.get("Name", "")

        # Connections
        self._delete_button.clicked.connect(self._on_delete_pressed)
        self._cancel_button.clicked.connect(self._on_cancel_pressed)

        preview_base64 = data.get("Preview", "")
        if preview_base64:
            byte_array = QByteArray.fromBase64(preview_base64.encode("utf-8"))
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array)

            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self._image_label.setPixmap(scaled_pixmap)

    def enterEvent(self, event):
        if not self._settings_visible:
            self.setStyleSheet("#shape_prefab_frame {background-color: rgba(245, 245, 245, 10);}")

    def leaveEvent(self, event):
        self.setStyleSheet("#shape_prefab_frame {background-color: transparent;}")
        self._set_settings_visible(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._set_settings_visible(True)
        if not self._settings_visible and event.button() == Qt.MouseButton.LeftButton:
            self.instanceRequested.emit(self._name)

        super().mousePressEvent(event)

    def _set_settings_visible(self, visible: bool):
        self._delete_button.setVisible(visible)
        self._cancel_button.setVisible(visible)
        self._settings_visible = visible

    @Slot()
    def _on_cancel_pressed(self):
        self._set_settings_visible(False)

    @Slot()
    def _on_delete_pressed(self):
        self.deleteRequested.emit(self._name)

class QPrefabScroll(QWidget):
    instanceRequested = Signal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._save_path: str | None = None

        base_path = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(base_path, "../../shape_prefabs.json")

        if os.path.exists(save_path):
            self._save_path = save_path

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Frame
        self._frame = QFrame(self)
        self._frame.setFixedWidth(600)
        self._frame.setMinimumHeight(150)
        self._frame.setProperty("class", "primary_frame")
        main_layout.addWidget(self._frame)

        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)

        # Scroll area
        self._scroll_area = QScrollArea(self._frame)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_layout = QHBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(15)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._scroll_layout.addStretch()

        self._scroll_area.setWidget(self._scroll_content)
        frame_layout.addWidget(self._scroll_area)

        self._load_prefabs()

    def _load_prefabs(self):
        if not self._save_path:
            return

        with open(self._save_path, 'r') as file:
            loaded = json.load(file)

            if isinstance(loaded, dict):
                existing = loaded
            else:
                existing = {"Shapes": loaded}

            for prefab_data in existing["Shapes"]:
                self.add_prefab(prefab_data, update_save=False)

    @Slot(str)
    def _on_instance_requested(self, name: str):
        if self._save_path is None:
            return

        with open(self._save_path, 'r') as file:
            loaded = json.load(file)

            for shape in loaded["Shapes"]:
                if shape.get("Name") == name:
                    data = {"Vertices": shape.get("Vertices")}
                    self.instanceRequested.emit(data)
                    break


    def add_prefab(self, data: dict, update_save: bool = True):
        if "Name" not in data:
            return
        simplified_data = {"Name": data.get("Name"), "Preview": data.get("Preview")}
        prefab = QShapePrefab(simplified_data)
        prefab.deleteRequested.connect(self._delete_prefab)
        prefab.instanceRequested.connect(self._on_instance_requested)
        count = self._scroll_layout.count()
        self._scroll_layout.insertWidget(count - 1, prefab)

        if update_save:
            self._update_save_path(data)

    def _update_save_path(self, data: dict):
        if not self._save_path:
            return

        existing = {"Shapes": []}
        with open(self._save_path, 'r') as file:
            loaded = json.load(file)

            if isinstance(loaded, dict):
                existing = loaded

                if "Shapes" not in existing:
                    existing["Shapes"] = []

        new_name = data.get("Name")
        for existing_prefab in existing["Shapes"]:
            print(existing_prefab)
            if existing_prefab.get("Name") == new_name:
                return

        existing["Shapes"].append(data)

        with open(self._save_path, 'w') as file:
            json.dump(existing, file, indent=4)

    @Slot(str)
    def _delete_prefab(self, name: str):
        sender = self.sender()
        if sender:
            self._scroll_layout.removeWidget(sender)
            sender.deleteLater()
            self._delete_from_save(name)

    def _delete_from_save(self, name: str):
        if not self._save_path:
            return

        with open(self._save_path, 'r') as file:
            existing = json.load(file)

        if isinstance(existing, dict) and "Shapes" in existing:
            existing["Shapes"] = [shape for shape in existing["Shapes"] if shape.get("Name") != name]

            with open(self._save_path, 'w') as file:
                json.dump(existing, file, indent=4)