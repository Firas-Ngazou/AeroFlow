import os
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Slot, QObject

from dev.user_interface.management.project_page import ProjectPage
from dev.user_interface.management.q_custom_window_frame import QCustomTitleBar
from configparser import ConfigParser

class ProjectState(Enum):
    DEFAULT = 0
    NEW = 1
    SAVED = 2
    NONE = 3

class ProjectManager(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._current_project: ProjectPage | None = None
        self._project_state = ProjectState.NONE
        self._project_title_bar: QCustomTitleBar | None = None

        self._ini_config = ConfigParser()
        self._ini_path = None

        base_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_path, "../../aeroflow.ini")

        if os.path.exists(path):
            self._ini_config.read(path)
            self._ini_path = path
        else: print(f"No aeroflow.ini file found at {path}. Saves may not work as intended.")

    def __ini_connections(self):
        self._current_project.qualityChanged.connect(
            lambda y: self._save_ini_number("Simulation", "Quality", y))
        self._current_project.windSpeedChanged.connect(
            lambda y: self._save_ini_number("Simulation", "Wind_speed", y))
        self._current_project.constraintChanged.connect(
            lambda y: self._save_ini_string("Optimization", "Constraint_method", y)
        )
        self._current_project.iterationsChanged.connect(
            lambda y: self._save_ini_number("Optimization", "Iterations", y)
        )
        self._current_project.thresholdChanged.connect(
            lambda y: self._save_ini_number("Optimization", "Constraint_threshold", y)
        )

    @property
    def current_project(self) -> ProjectPage | None:
        return self._current_project
    @current_project.setter
    def current_project(self, project: ProjectPage | None):
        if project is not None:
            self._current_project = project
            self._current_project.saveProject.connect(self.save_project)
            self.__load_ini_values()
            self.__ini_connections()

            self._project_state = self._get_project_state()
            self._project_title_bar = project.title_bar

            self._project_title_bar.closeBtn.clicked.disconnect(self._project_title_bar.window().close)
            self._project_title_bar.closeBtn.clicked.connect(self._on_close_clicked)

        else:
            self._current_project = None
            self._project_state = self._get_project_state()
            self._project_title_bar = None

    @property
    def project_state(self) -> ProjectState:
        return self._project_state
    @project_state.setter
    def project_state(self, state: ProjectState):
        self._project_state = state

    @Slot()
    def _on_close_clicked(self):
        if self._project_state is ProjectState.NEW: self._project_title_bar.window().close()
        else: self._current_project.save_warning.show()

    def _get_project_state(self):
        if self._current_project is None: return ProjectState.NONE
        return ProjectState.DEFAULT # For testing purposes - Will be changed later

    def save_project(self):
        # Opens file dialog & Saves the project
        ...

    def open_project(self):
        # Opens file dialog & Loads the project
        ...

    @Slot(float, int)
    def _save_ini_number(self, category: str, parameter: str, value: float | int):
        print(f"Saving {category} {parameter} to {value:.2f}")
        self._ini_config[category][parameter] = str(f"{value}")
        with open(self._ini_path, 'w') as configfile:
            self._ini_config.write(configfile)

    @Slot(str)
    def _save_ini_string(self, category: str, parameter: str, value: str):
        print(f"Saving {category} {parameter} to {value}")
        self._ini_config[category][parameter] = value
        with open(self._ini_path, 'w') as configfile:
            self._ini_config.write(configfile)

    def __load_ini_values(self):
        self._ini_config.read(self._ini_path)

        quality = self._ini_config.getfloat("Simulation", "Quality")
        wind_speed = self._ini_config.getfloat("Simulation", "Wind_speed")
        constraint_method = self._ini_config.get("Optimization", "Constraint_method")
        iterations = self._ini_config.getint("Optimization", "Iterations")
        threshold = self._ini_config.getint("Optimization", "Constraint_threshold")

        self._current_project.quality = quality
        self._current_project.wind_speed = wind_speed
        self._current_project.constraint_method = constraint_method
        self._current_project.iterations = iterations
        self._current_project.threshold = threshold