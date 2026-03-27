import sys

from PySide6.QtCore import Signal, QSize, Slot, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QApplication

from q_editor import QEditor, StateManager, Shape

class QToolBar(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.__cursor_state = StateManager.CursorState.DEFAULT
        self.__settings_last_state = False

        # setup
        primary_frame = QFrame(self)
        primary_frame.setObjectName("tool_bar_primary_frame")
        primary_frame.setStyleSheet("""
            #tool_bar_primary_frame {
                background-color: #222;
                border: 1px solid #F5F5F5; 
                border-radius: 26px;
            }""")
        primary_frame.setFixedHeight(56)
        primary_layout = QHBoxLayout(primary_frame)
        primary_layout.setContentsMargins(5, 5, 5, 5)

        # default button
        cursor_icon = QIcon("../icons/cursor_icon_black.png")
        self.__default_button = QPushButton()
        self.__default_button.setCheckable(True)
        self.__default_button.setChecked(True)
        self.__default_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #1D1D1D;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 22px;
            }

            :hover {
                background-color: #e0e0e0;
            }

            :pressed {
                background-color: #c0c0c0;
            }

            :checked {
                background-color: #A6A6A6;
            }
            """)
        self.__default_button.setIcon(cursor_icon)
        self.__default_button.setIconSize(QSize(21, 21))
        self.__default_button.setFixedSize(44, 44)

        # pen button
        pen_icon = QIcon("../icons/pen_icon_black.png")
        self.__pen_button = QPushButton()
        self.__pen_button.setCheckable(True)
        self.__pen_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #1D1D1D;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 22px;
            }

            :hover {
                background-color: #e0e0e0;
            }

            :pressed {
                background-color: #c0c0c0;
            }
            :checked {
                background-color: #A6A6A6;
            }
            """)
        self.__pen_button.setIcon(pen_icon)
        self.__pen_button.setIconSize(QSize(21, 21))
        self.__pen_button.setFixedSize(44, 44)

        # play button
        play_icon = QIcon("../icons/play_icon_black.png")
        self.__play_button = QPushButton()
        self.__play_button.setCheckable(True)
        self.__play_button.setStyleSheet("""
            QPushButton {
                background-color: #92B28A;
                color: #1D1D1D;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 22px;
            }

            :hover {
                background-color: #73976A;
            }

            :pressed {
                background-color: #73976A;
            }

            :checked {
                background-color: #BA7475;
            }
            """)
        self.__play_button.setIcon(play_icon)
        self.__play_button.setIconSize(QSize(21, 21))
        self.__play_button.setFixedSize(44, 44)

        # optimize button
        optimize_icon = QIcon("../icons/optimize_icon_black.png")
        optimize_button = QPushButton()
        optimize_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #1D1D1D;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 22px;
            }

            :hover {
                background-color: #e0e0e0;
            }

            :pressed {
                background-color: #c0c0c0;
            }
            """)
        optimize_button.setIcon(optimize_icon)
        optimize_button.setIconSize(QSize(21, 21))
        optimize_button.setFixedSize(44, 44)

        # pause button
        pause_icon = QIcon("../icons/pause_icon_black.png")
        self.__pause_button = QPushButton()
        self.__pause_button.setCheckable(True)
        self.__pause_button.setVisible(False)
        self.__pause_button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFCACB;
                        color: #1D1D1D;
                        padding-left: 15px;
                        padding-right: 15px;
                        border-radius: 22px;
                    }

                    :hover {
                        background-color: #BA7475;
                    }

                    :pressed {
                        background-color: #BA7475;
                    }

                    :checked {
                        background-color: #92B28A;
                    }
                    """)
        self.__pause_button.setIcon(pause_icon)
        self.__pause_button.setIconSize(QSize(21, 21))
        self.__pause_button.setFixedSize(44, 44)

        # settings button
        settings_icon = QIcon("../icons/settings_icon_black.png")
        self.__settings_button = QPushButton()
        self.__settings_button.setCheckable(True)
        self.__settings_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #1D1D1D;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 22px;
            }

            :hover {
                background-color: #e0e0e0;
            }

            :pressed {
                background-color: #c0c0c0;
            }

            :checked {
                background-color: #A6A6A6;
            }
            """)
        self.__settings_button.setIcon(settings_icon)
        self.__settings_button.setIconSize(QSize(21, 21))
        self.__settings_button.setFixedSize(44, 44)

        primary_layout.addWidget(self.__default_button)
        primary_layout.addWidget(self.__pen_button)
        primary_layout.addWidget(self.__play_button)
        primary_layout.addWidget(optimize_button)
        primary_layout.addWidget(self.__settings_button)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self.__pause_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        root_layout.addWidget(primary_frame)
        self.setLayout(root_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QToolBar()
    window.show()
    sys.exit(app.exec())