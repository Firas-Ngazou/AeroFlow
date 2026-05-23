import json

import PySide6
from __feature__ import snake_case, true_property  # type: ignore[import-not-found]

import dev.user_interface.tools.q_wrapper as q_wrapper
q_wrapper.apply_all_wrappers()

from PySide6.QtCore import Qt, QByteArray, QMargins, Signal
from PySide6.QtGui import QFontDatabase, QPalette, QColor, QIcon, QPixmap, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout, QStackedWidget, QMainWindow, QLabel, \
    QFrame

class QProjectPreview(QWidget):
    selected = Signal(str)

    def __init__(self, path: str, preview_width: int = 390, parent: QWidget | None = None):
        super().__init__(parent)

        self.set_fixed_size(400, 250)
        self.mouse_tracking = True

        self._preview_width = preview_width
        self._preview_height = int(self._preview_width*(1/2.39))
        self._path = path

        # Fonts
        header_font = QFont("JetBrains Mono", 12)
        header_font.set_bold(True)
        description_font = QFont("JetBrains Mono", 9)
        description_font.set_italic(True)

        # Header
        self._header = QLabel("  Header")
        self._header.style_sheet = "background-color: transparent;"
        self._header.font = header_font
        self._header.set_fixed_height(50)
        self._header.alignment = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Description
        self._description = QLabel("   Description")
        self._description.style_sheet = "background-color: transparent;"
        self._description.font = description_font
        self._description.set_fixed_height = 20

        # Preview
        self._preview_label = QLabel("No preview available.")
        self._preview_label.style_sheet = "background-color: transparent;"
        self._preview_label.alignment = Qt.AlignmentFlag.AlignCenter
        self._preview_label.set_fixed_size(self._preview_width, self._preview_height)
        self._preview_pixmap: QPixmap | None = None

        # Frame
        self._primary_frame = QFrame()
        self._primary_frame.set_fixed_size(self.size)
        self._primary_frame.set_property("class", "primary_frame")
        self.style_sheet = "background-color: transparent;"

        # Layout
        self._primary_layout = QVBoxLayout(self._primary_frame)
        self._primary_layout.add_widget(self._preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._primary_layout.add_widget(self._header, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._primary_layout.add_widget(self._description, alignment=Qt.AlignmentFlag.AlignHCenter |
                                                                    Qt.AlignmentFlag.AlignTop)
        self._primary_layout.spacing = 0
        self._primary_layout.add_stretch()
        self._primary_layout.set_contents_margins(0, 0, 0, 0)

        root_layout = QVBoxLayout(self)
        root_layout.add_widget(self._primary_frame)
        root_layout.set_contents_margins(0, 0, 0, 0)
        root_layout.add_stretch()

        self._init_config()

    def mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_selected()

    def enter_event(self, event):
        self.style_sheet = "background-color: rgba(245, 245, 245, 10);"

    def leave_event(self, event):
        self.style_sheet = "background-color: transparent;"

    def _on_selected(self):
        self.selected.emit(self._path)

    def _get_config(self) -> list[QPixmap|str]:
        config = []
        with open(self._path, "r") as file:
            save = json.load(file)

        preview_base64 = save["Drawing"]["Preview"]
        encoded_preview = QByteArray.from_base64(preview_base64.encode("utf-8"))

        raw_preview = QPixmap()
        raw_preview.load_from_data(encoded_preview)

        rounded_preview = QPixmap(raw_preview.size())
        rounded_preview.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded_preview)
        painter.set_render_hint(QPainter.RenderHint.Antialiasing)
        painter.set_render_hint(QPainter.RenderHint.SmoothPixmapTransform)

        radius = 8
        painter_path = QPainterPath()
        painter_path.add_rounded_rect(raw_preview.rect(), radius, radius)

        painter.set_clip_path(painter_path)
        painter.draw_pixmap(0, 0, raw_preview)
        painter.end()

        config.append(rounded_preview)

        header = save["General"]["Project_name"]
        config.append(header)

        description = save["General"]["Project_description"]
        config.append(description)

        return config

    def _init_config(self):
        preview, header, description = self._get_config()

        scaled_preview = preview.scaled(self._preview_width, self._preview_height, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
        self._preview_pixmap = scaled_preview
        self._preview_label.pixmap = self._preview_pixmap

        self._header.text = f"{header}"
        self._description.text = f"{description}"

    @property
    def project_path( self ) -> str:
        return self._path