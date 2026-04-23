import os
import sys
from dev.user_interface import ressources_rc

from qframelesswindow import TitleBar

from PySide6.QtGui import QFontDatabase, QPalette, QColor, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QStackedWidget

from dev.user_interface.management.q_custom_window_frame import FramelessWindow, QCustomTitleBar
from dev.user_interface.management.project_page import ProjectPage
from dev.user_interface.management.home_page import HomePage

from dev.core.project_manager import ProjectManager


class AeroFlow:
    def __init__(self):
        self._window = FramelessWindow()
        self._window.resize(1920, 1080)

        self._home_page_title_bar = TitleBar(self._window)
        self._home_page_title_bar.hide()
        self._home_page_title_bar.minBtn.setNormalColor(QColor("#F5F5F5"))
        self._home_page_title_bar.maxBtn.setNormalColor(QColor("#F5F5F5"))
        self._home_page_title_bar.closeBtn.setNormalColor(QColor("#F5F5F5"))
        self._home_page_title_bar.minBtn.setHoverColor(QColor("#F5F5F5"))
        self._home_page_title_bar.maxBtn.setHoverColor(QColor("#F5F5F5"))

        self._project_page_title_bar = QCustomTitleBar(self._window)
        self._project_page_title_bar.icon = QIcon(":/res/app_logo.png")
        self._project_page_title_bar.hide()

        self._stack = QStackedWidget(self._window)

        self._home_page = HomePage(parent=self._window)
        self._stack.addWidget(self._home_page)

        self._project_page: ProjectPage | None = None
        self._project_manager = ProjectManager()

        self._primary_layout = QHBoxLayout(self._window)
        self._primary_layout.setSpacing(0)
        self._primary_layout.setContentsMargins(0, 32, 0, 0)
        self._primary_layout.addWidget(self._stack)

        self._home_page.newProjectPressed.connect(self.__show_project_page)

        self.__show_home_page()
        self._window.show()

    def __show_home_page(self):
        self._project_manager.current_project = None

        self._home_page.show()
        self._project_page_title_bar.hide()

        self._window.setTitleBar(self._home_page_title_bar)
        self._home_page_title_bar.show()

        self._stack.setCurrentWidget(self._home_page)

    def __show_project_page(self):
        if self._project_page is not None:
            self._stack.removeWidget(self._project_page)
            self._project_page.deleteLater()

        self._window.setTitleBar(self._project_page_title_bar)
        self._home_page_title_bar.hide()

        self._project_page = ProjectPage(self._window)
        self._project_page.homeRequested.connect(self.__show_home_page)
        self._stack.addWidget(self._project_page)
        self._stack.setCurrentWidget(self._project_page)

        self._project_manager.current_project = self._project_page

        self._project_page_title_bar.resize(self._window.width(), 32)
        self._project_page_title_bar.show()

class ThemeManager:
    def __init__(self, q_app: QApplication):
        self._q_app = q_app

        self._load_custom_fonts()
        self._load_styles()
        self._palette: QPalette | None = None
        self._apply_dark_palette()

    @staticmethod
    def _load_custom_fonts():
        QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Regular.ttf")
        QFontDatabase.addApplicationFont(":/res/JetBrainsMono-Bold.ttf")
        QFontDatabase.addApplicationFont(":/res/Author-Regular.otf")
        QFontDatabase.addApplicationFont(":/res/Author-Bold.otf")

    def _apply_dark_palette(self) -> None:
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#F5F5F5"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#1D1D1D10"))
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#1D1D1D"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1D1D1D"))

        self._q_app.setPalette(dark_palette)

        self._palette = dark_palette

        self._inherit_palette(self._q_app)

    def _inherit_palette(self, q_widget: QWidget | QApplication):
        for child in q_widget.findChildren(QWidget):
            child.setPalette(self._palette)
            self._inherit_palette(child)

    def _load_styles(self) -> None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        styles_path = os.path.join(base_path, "../user_interface/styles.qss")

        if os.path.exists(styles_path):
            with open(styles_path, "r") as file:
                self._q_app.setStyleSheet(file.read())

        else:
            print("'styles.qss' file was not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ThemeManager(app)

    aeroflow = AeroFlow()
    sys.exit(app.exec())