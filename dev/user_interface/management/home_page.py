import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QHBoxLayout, QLabel, \
    QScrollArea, QGridLayout, QPushButton

from dev.user_interface.components.q_seperators import QHSeperator
from dev.user_interface.management.q_custom_window_frame import FramelessWindow
from dev.user_interface.management.q_project_preview import QProjectPreview

class QHomePageSettingsPB(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.setText(text)
        self.setFont(QFont("JetBrains Mono", 12))
        self.setProperty("class", "titlebar_settings_pb")
        self.setFixedSize(100, 32)

class HomePage(QWidget):
    newProjectPressed = Signal()
    openProjectPressed = Signal()

    def __init__(self, preview_width: int = 300, parent: FramelessWindow|None = None):
        super().__init__(parent)

        self.resize(1920, 500)
        self.setMinimumWidth(1080)

        # New project button
        self._new_project_pb = QHomePageSettingsPB("Nouveau")

        # Open project button
        self._open_project_pb = QHomePageSettingsPB("Ouvrir")

        # Software name
        self._software_name = QLabel("AeroFlow")
        self._software_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._software_name.setFont(QFont("JetBrains Mono", 24))
        self._software_name.setFixedWidth(500)

        # ScrollArea
        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("home_page_scroll_area")
        self._scroll_area.setStyleSheet("#home_page_scroll_area {border: none;}")
        self._scroll_area.setMinimumHeight(self.height())
        self._scroll_area.setWidgetResizable(True)
        self._scroll_content = QWidget()
        self._scroll_area.setWidget(self._scroll_content)

        self._scroll_content_layout = QGridLayout(self._scroll_content)
        self._scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Layout
        self._settings_layout = QHBoxLayout()
        self._settings_layout.setSpacing(10)
        self._settings_layout.setContentsMargins(0, 0, 0, 0)
        self._settings_layout.addStretch()

        h_seperator_left = QHSeperator()
        h_seperator_left.setFixedWidth(200)
        self._settings_layout.addWidget(h_seperator_left, alignment=Qt.AlignmentFlag.AlignCenter)
        self._settings_layout.addWidget(self._new_project_pb, alignment=Qt.AlignmentFlag.AlignCenter)

        h_seperator_center = QHSeperator()
        h_seperator_center.setFixedWidth(50)
        self._settings_layout.addWidget(h_seperator_center, alignment=Qt.AlignmentFlag.AlignCenter)
        self._settings_layout.addWidget(self._open_project_pb, alignment=Qt.AlignmentFlag.AlignCenter)

        h_seperator_right = QHSeperator()
        h_seperator_right.setFixedWidth(200)
        self._settings_layout.addWidget(h_seperator_right, alignment=Qt.AlignmentFlag.AlignCenter)
        self._settings_layout.addStretch()

        self._secondary_layout = QVBoxLayout()
        self._secondary_layout.setContentsMargins(10, 10, 10, 10)
        self._secondary_layout.addWidget(self._software_name, alignment=Qt.AlignmentFlag.AlignCenter)
        self._secondary_layout.addLayout(self._settings_layout)
        self._secondary_layout.addWidget(self._scroll_area)

        self._primary_layout = QHBoxLayout(self)
        self._primary_layout.setContentsMargins(0, 0, 0, 0)
        self._primary_layout.setSpacing(10)
        self._primary_layout.addLayout(self._secondary_layout)

        self._new_project_pb.clicked.connect(self.newProjectPressed.emit)
        self._open_project_pb.clicked.connect(self.openProjectPressed.emit)

        # ScrollArea setup
        self._max_column = 4
        self._previous_max_row = 0
        self._current_column = 0
        self._current_row = 0

        self.add_project("C:/Users/user/Documents/AeroFlow/Projects/Test")

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        width = self.rect().width()
        self._max_column = int(width) // 300
        self._rearrange()

    def add_project(self, project_path: str):
        project_preview = QProjectPreview(project_path)
        self._scroll_content_layout.addWidget(project_preview, self._current_row, self._current_column)

        self._update_current_values()

    def _rearrange(self):
        if self._scroll_content_layout.count() == 0: return

        self._current_column = 0
        self._current_row = 0

        widgets = []
        while self._scroll_content_layout.count():
            item = self._scroll_content_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                self._scroll_content_layout.removeWidget(widget)
                widgets.append(widget)

        for widget in widgets:
            self._scroll_content_layout.addWidget(widget, self._current_row, self._current_column)

            self._update_current_values()

    def _update_current_values(self):
        if self._current_column == self._max_column - 1:
            self._current_column = 0
            self._current_row += 1
        else:
            self._current_column += 1
#
# class ThemeManager:
#     def __init__(self, q_app: QApplication):
#         self._q_app = q_app
#
#         self._load_custom_fonts()
#         self._load_styles()
#         self._palette: QPalette | None = None
#         self._apply_dark_palette()
#
#     @staticmethod
#     def _load_custom_fonts():
#         QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Regular.ttf")
#         QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Bold.ttf")
#         QFontDatabase.addApplicationFont(":/res/Author-Regular.otf")
#         QFontDatabase.addApplicationFont(":/res/Author-Bold.otf")
#
#     def _apply_dark_palette(self) -> None:
#         dark_palette = QPalette()
#
#         dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#F5F5F5"))
#         dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#1D1D1D10"))
#         dark_palette.setColor(QPalette.ColorRole.Window, QColor("#1D1D1D"))
#         dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1D1D1D"))
#
#         self._q_app.setPalette(dark_palette)
#
#         self._palette = dark_palette
#
#         self._inherit_palette(self._q_app)
#
#     def _inherit_palette(self, q_widget: QWidget | QApplication):
#         for child in q_widget.findChildren(QWidget):
#             child.setPalette(self._palette)
#             self._inherit_palette(child)
#
#     def _load_styles(self) -> None:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#         styles_path = os.path.join(base_path, "styles.qss")
#
#         if os.path.exists(styles_path):
#             with open(styles_path, "r") as file:
#                 self._q_app.setStyleSheet(file.read())
#
#         else:
#             print("'styles.qss' file was not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # ThemeManager(app)
    window = HomePage()
    window.show()
    sys.exit(app.exec())