from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QPalette, QColor, QIcon, QPixmap, QFont
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout, QStackedWidget, QMainWindow, QLabel, \
    QFrame

class QProjectPreview(QWidget):
    def __init__(self, path: str, preview_width: int = 300, parent: QWidget | None = None):
        super().__init__(parent)

        self.setFixedSize(400, 250)
        self.setMouseTracking(True)

        self._preview_width = preview_width
        self._preview_height = int(self._preview_width*(9/16))
        self._path = path

        # Fonts
        header_font = QFont("JetBrains Mono", 12)
        header_font.setBold(True)
        description_font = QFont("JetBrains Mono", 9)
        description_font.setItalic(True)

        # Header
        self._header = QLabel("  Header")
        self._header.setStyleSheet("background-color: transparent;")
        self._header.setFont(header_font)
        self._header.setFixedHeight(50)
        self._header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Description
        self._description = QLabel("   Description")
        self._description.setStyleSheet("background-color: transparent;")
        self._description.setFont(description_font)
        self._description.setFixedHeight(20)

        # Preview
        self._preview_label = QLabel("No preview available.")
        self._preview_label.setStyleSheet("background-color: transparent;")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFixedSize(self._preview_width, self._preview_height)
        self._preview_pixmap: QPixmap | None = None

        # Frame
        self._primary_frame = QFrame()
        self._primary_frame.setFixedSize(self.size())
        self._primary_frame.setProperty("class", "primary_frame")
        self.setStyleSheet("background-color: transparent;")

        # Layout
        self._primary_layout = QVBoxLayout(self._primary_frame)
        self._primary_layout.addWidget(self._preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._primary_layout.addWidget(self._header, alignment=Qt.AlignmentFlag.AlignLeft)
        self._primary_layout.addWidget(self._description, alignment=Qt.AlignmentFlag.AlignLeft |
                                                                    Qt.AlignmentFlag.AlignTop)
        self._primary_layout.setSpacing(0)
        self._primary_layout.addStretch()
        self._primary_layout.setContentsMargins(0, 0, 0, 0)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self._primary_frame)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_selected()

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgba(245, 245, 245, 10);")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: transparent;")

    def _on_selected(self):
        ...

    def set_preview(self, preview: QPixmap):
        scaled_preview = preview.scaled(self._preview_width, self._preview_height, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
        self._preview_pixmap = scaled_preview
        self._preview_label.setPixmap(self._preview_pixmap)

if __name__ == "__main__":
    app = QApplication([])
    window = QMainWindow()
    project_preview = QProjectPreview(parent=window)
    window.show()
    app.exec()