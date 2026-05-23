from datetime import date

import numpy as np
from PySide6.QtCore import Qt, Signal, QPoint, Slot, QThread, QMetaObject, Q_ARG
from PySide6.QtGui import QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame, QLabel, QLineEdit

from dev.physics_engine.simulation_engine import SimulationEngine
from dev.user_interface.analysis.q_analysis_tabs import QAnalysisWidget
from dev.user_interface.canvas.q_animation_controller import QSimController, SimImageType
from dev.user_interface.canvas.q_settings_tab import QSettingsSideBar
from dev.user_interface.floating.q_floating_content import QFloatingWarning
from dev.physics_engine.vector_obstacle import VectorObstacle
from dev.user_interface.canvas.q_state_manager import QStateManager
from dev.user_interface.canvas.q_editor import QEditor
from dev.user_interface.canvas.q_tool_bar import QToolBar
from dev.user_interface.management.q_custom_window_frame import FramelessWindow, QCustomTitleBar

class ProjectPage(QWidget):
    saveProject = Signal(dict)
    saveAsProject = Signal(dict)
    homeRequested = Signal()
    constraintChanged = Signal(str)
    iterationsChanged = Signal(int)
    thresholdChanged = Signal(int)

    qualityChanged = Signal(float)
    windSpeedChanged = Signal(float)
    viscosityChanged = Signal(float)
    liveEditStateChanged = Signal(int)
    velocityStateChanged = Signal(int)
    densityStateChanged = Signal(int)
    streamlinesStateChanged = Signal(int)
    curlStateChanged = Signal(int)
    streamlineCountChanged = Signal(int)
    staircaseStateChanged = Signal(int)

    liveEditVerticesChanged = Signal(np.ndarray)

    jsonSettingsChanged = Signal()

    vectorDrawingChanged = Signal()
    saveWarningYesPressed = Signal()
    saveWarningNoPressed = Signal()

    runSimulation = Signal(list)

    def __init__(self, parent: FramelessWindow) -> None:
        super().__init__(parent)

        self._minimum_window_width = 600
        self._minimum_window_height = 250
        self._maximum_window_width = 19200
        self._maximum_window_height = 10800

        self._initial_res = 1080
        self.resize(int((16/9)*self._initial_res), self._initial_res)
        self.setMinimumWidth(self._minimum_window_width)
        self.setMinimumHeight(self._minimum_window_height)
        self._allocation = 5000

        self._editor: QEditor
        self._sim_controller: QSimController
        self._state_manager = QStateManager(self)
        self._window = parent

        self._title_bar: QCustomTitleBar = self._window.titleBar
        self._analysis_tab = QAnalysisWidget(QPoint(0, 0), self)
        self._analysis_tab.hide()

        self._sim_thread = QThread()
        self._simulation_engine = SimulationEngine()
        self._simulation_engine.moveToThread(self._sim_thread)

        self.__initialize_canvas()
        self.__initialize_title_bar()
        self.__initialize_connections()

        self._simulation_engine.progressUpdated.connect(self._on_sim_progressed)
        self._simulation_engine.statusMessageUpdated.connect(self._analysis_tab.set_sim_info_label)
        self._simulation_engine.iterationCompleted.connect(self._sim_controller.add_sim_data)
        self._simulation_engine.maxStepUpdated.connect(self._sim_controller.set_max_steps)
        self._simulation_engine.dragCoefUpdated.connect(lambda y: self._analysis_tab.set_drag_coef_value(f"{y:.2f}"))
        self._simulation_engine.liftCoefUpdated.connect(lambda y: self._analysis_tab.set_lift_coef_value(f"{y:.2f}"))
        self._simulation_engine.reynoldsUpdated.connect(lambda y: self._analysis_tab.set_reynolds_number_value(
            f"{y:.2f}"))
        self._simulation_engine.machUpdated.connect(lambda y: self._analysis_tab.set_mach_number_value(f"{y:.2f}"))
        self._simulation_engine.kineticEnergyUpdated.connect(lambda y: self._analysis_tab.set_kinetic_energy_value(
            f"{y:.2f}"))
        self._simulation_engine.pressureDropUpdated.connect(lambda y: self._analysis_tab.set_pressure_drop_value(
            f"{y:.2f}"))
        self._simulation_engine.massUpdated.connect(lambda y: self._analysis_tab.set_total_mass_value(f"{y:.2f}"))
        self._simulation_engine.enstrophyUpdated.connect(lambda y: self._analysis_tab.set_total_enstrophy_value(
            f"{y:.2f}"))
        self._simulation_engine.maxVorticityUpdated.connect(lambda y: self._analysis_tab.set_max_vorticity_value(
            f"{y:.2f}"))
        # self._simulation_engine.finished.connect(self._on_sim_finished)
        self.runSimulation.connect(self._simulation_engine.run)
        self.liveEditVerticesChanged.connect(self._simulation_engine.queue_live_edit_vertices,
                                             Qt.ConnectionType.DirectConnection)

        self._sim_thread.start()

        self._primary_layout = QVBoxLayout(self)
        self._primary_layout.setContentsMargins(0, 0, 0, 0)
        self._primary_layout.addWidget(self._editor)

    def __initialize_canvas(self) -> None:
        self._editor = QEditor(self._state_manager)
        self._editor.switch_cursor(QStateManager.CursorState.DEFAULT)

        self._sim_controller = QSimController()
        self._sim_controller.hide()

        self._tool_bar = QToolBar(self._state_manager)
        self._settings_side_bar = QSettingsSideBar()

        self._lower_layout = QHBoxLayout()
        self._lower_layout.addWidget(self._tool_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._secondary_layout = QVBoxLayout(self._editor)
        self._secondary_layout.setContentsMargins(5, 5, 5, 0)
        self._secondary_layout.addWidget(self._settings_side_bar,
                                         alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self._secondary_layout.addStretch()
        self._secondary_layout.addWidget(self._sim_controller, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._secondary_layout.addLayout(self._lower_layout)

    def __initialize_title_bar(self) -> None:
        self._save_warning = QFrame(self)
        self._save_warning.setObjectName("save_warning")
        self._save_warning.setStyleSheet("#save_warning { background-color: rgba(245, 245, 245, 70);}")
        self._save_warning_window = QFloatingWarning(QPoint(int(self.width()/2), int(self.height()/2)),
                                                     "Attention",
                                                     "Quitter sans sauvegarder vos modifications "
                                                     "risque de\n"
                                                     "résulter en une perte totale de votre travail.\n\n"
                                                     "Êtes-vous sûr de vouloir continuer ?",
                                                     self._save_warning)
        self._save_warning.hide()

    def __initialize_connections(self) -> None:
        """
        Sets up all necessary signal-slot connections for the class and initializes
        shortcuts. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.constraintChanged.connect(self.constraintChanged.emit)
        self._settings_side_bar.iterationsChanged.connect(self.iterationsChanged.emit)
        self._settings_side_bar.thresholdChanged.connect(self.thresholdChanged.emit)

        self._settings_side_bar.qualityChanged.connect(self.qualityChanged.emit)
        self._settings_side_bar.windSpeedChanged.connect(self.windSpeedChanged.emit)
        self._settings_side_bar.viscosityChanged.connect(self._on_viscosity_changed)
        self._settings_side_bar.velocityStateChanged.connect(self._on_velocity_state_changed)
        self._settings_side_bar.liveEditStateChanged.connect(self._on_live_edit_state_changed)
        self._settings_side_bar.densityStateChanged.connect(self._on_density_state_changed)
        self._settings_side_bar.streamlinesStateChanged.connect(self._on_streamlines_state_changed)
        self._settings_side_bar.curlStateChanged.connect(self._on_curl_state_changed)
        self._settings_side_bar.streamlineCountChanged.connect(self._on_streamline_count_changed)
        self._settings_side_bar.staircaseStateChanged.connect(self._on_staircase_state_changed)
        # self._settings_side_bar.saveRequested.connect(self._on_save_sim_requested)
        # self._settings_side_bar.clearRequested.connect(self._on_clear_sim_requested)

        self._tool_bar.playPressed.connect(self._on_play_pressed)
        self._tool_bar.stopPressed.connect(self.on_stop_pressed)
        self._tool_bar.instanceRequested.connect(self._editor.add_shape)

        self._sim_controller.showPixmapRequested.connect(self._editor.display_pixmap)
        self._sim_controller.pauseRequested.connect(self._on_sim_pause_requested)
        self._sim_controller.resumeRequested.connect(self._on_sim_resume_requested)

        self._editor.vectorDrawingChanged.connect(self._on_vector_drawing_changed)
        self._editor.saveShapeRequested.connect(self._on_save_shape_requested)
        self._editor.inEditMode.connect(self._on_in_edit_mode)
        self._editor.optimizeRequested.connect(self._on_optimize_start)

        self._state_manager.cursorStateChanged.connect(self._on_cursor_state_changed)

        self._save_warning_window.yesPressed.connect(self.saveWarningYesPressed.emit)
        self._save_warning_window.noPressed.connect(self.saveWarningNoPressed.emit)

        self._title_bar.analysisPressed.connect(lambda y: self._on_analysis_pressed(y))
        self._title_bar.saveFileRequested.connect(self._on_save_project)
        self._title_bar.saveAsFileRequested.connect(self._on_save_as_project)
        self._title_bar.undoRequested.connect(self._on_undo_requested)
        self._title_bar.redoRequested.connect(self._on_redo_requested)
        self._title_bar.selectAllRequested.connect(self._on_select_all_requested)
        self._title_bar.deleteRequested.connect(self._on_delete_requested)

        self.qualityChanged.connect(self._sim_controller.set_reduction_factor)

        # Project saving
        self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self._save_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)

        self._save_shortcut.activated.connect(self._on_save_project)

    @Slot(bool)
    def _on_in_edit_mode(self, in_edit_mode: bool):
        self._title_bar.is_in_edit_mode = in_edit_mode

    @Slot(QStateManager.CursorState)
    def _on_cursor_state_changed(self, state: QStateManager.CursorState):
        self._editor.switch_cursor(state)
        self._tool_bar.update_cursor_state(state)

    @Slot()
    def _on_undo_requested(self):
        self._editor.undo()

    @Slot()
    def _on_redo_requested(self):
        self._editor.redo()

    @Slot()
    def _on_select_all_requested(self):
        self._editor.select_all()

    @Slot()
    def _on_delete_requested(self):
        self._editor.delete_all()

    @Slot()
    def _on_sim_pause_requested(self):
        self._simulation_engine.pause_requested = True

    @Slot()
    def _on_sim_resume_requested(self):
        self._simulation_engine.pause_requested = False

    @Slot(dict)
    def _on_save_shape_requested(self, data: dict) -> None:
        if "Name" in data and "Vertices" in data and "Preview" in data:
            prefab_data = {"Name": data.get("Name"), "Vertices": data.get("Vertices"), "Preview": data.get("Preview")}
            self._tool_bar.add_prefab_to_scroll(prefab_data)

    @Slot()
    def _on_vector_drawing_changed(self) -> None:
        """
        Handles the event when the vector drawing in the editor changes. - Generated by OpenAI's GPT 5.5
        """
        # self._force_reset_sim()
        self.vectorDrawingChanged.emit()
        if self._simulation_engine.live_edit:
            updated_vertices = self._editor.get_vertices()
            self.liveEditVerticesChanged.emit(updated_vertices.copy())

    @Slot(np.ndarray)
    def _on_optimize_start(self, vertices: np.ndarray) -> None:
        ...

    # def _force_reset_sim(self):
    #     self._sim_controller.save_requested = False
    #     self._sim_controller.request_clear()
    #     self._settings_side_bar.save_disabled = True
    #     self._settings_side_bar.clear_disabled = True

    # @Slot()
    # def _on_sim_finished(self):
    #     self._settings_side_bar.save_disabled = False
    #     self._settings_side_bar.update_save_info(f"{self._sim_controller.h5_size/1000000000:.1f}GB")

    @Slot(float)
    def _on_viscosity_changed(self, value: float) -> None:
        """
        Handles the event when the viscosity setting changes. - Generated by OpenAI's GPT 5.5
        """
        self.viscosityChanged.emit(value)
        self._simulation_engine.viscosity = value

    @Slot(int)
    def _on_live_edit_state_changed(self, state: int) -> None:
        """
        Handles the event when the live edit state changes. - Generated by OpenAI's GPT 5.5
        """
        self.liveEditStateChanged.emit(state)
        self._sim_controller.live_edit = state == 2
        self._simulation_engine.live_edit = state == 2
        self._tool_bar.live_edit = state == 2
        self.jsonSettingsChanged.emit()

    @Slot(int)
    def _on_velocity_state_changed(self, state: int) -> None:
        """
        Handles the event when the velocity state toggle changes. - Generated by OpenAI's GPT 5.5
        """
        self.velocityStateChanged.emit(state)
        self.jsonSettingsChanged.emit()
        self._update_image_type()

    @Slot(int)
    def _on_density_state_changed(self, state: int) -> None:
        """
        Handles the event when the density state toggle changes. - Generated by OpenAI's GPT 5.5
        """
        self.densityStateChanged.emit(state)
        self.jsonSettingsChanged.emit()
        self._update_image_type()

    @Slot(int)
    def _on_streamlines_state_changed(self, state: int) -> None:
        """
        Handles the event when the streamlines state toggle changes. - Generated by OpenAI's GPT 5.5
        """
        self.streamlinesStateChanged.emit(state)
        self.jsonSettingsChanged.emit()
        self._update_image_type()

    @Slot(int)
    def _on_curl_state_changed(self, state: int) -> None:
        """
        Handles the event when the curl state toggle changes. - Generated by OpenAI's GPT 5.5
        """
        self.curlStateChanged.emit(state)
        self.jsonSettingsChanged.emit()
        self._update_image_type()

    @Slot(int)
    def _on_staircase_state_changed(self, state: int) -> None:
        """
        Handles the event when the staircase state toggle changes. - Generated by OpenAI's GPT 5.5
        """
        self.staircaseStateChanged.emit(state)
        self._simulation_engine.staircase_effect = state != 2
        self.jsonSettingsChanged.emit()

    @Slot(int)
    def _on_streamline_count_changed(self, count: int) -> None:
        """
        Handles the event when the streamline count changes. - Generated by OpenAI's GPT 5.5
        """
        self.streamlineCountChanged.emit(count)
        self.jsonSettingsChanged.emit()
        self._sim_controller.streamline_count = count

    # @Slot()
    # def _on_save_sim_requested(self):
    #     self._settings_side_bar.save_disabled = True
    #     self._sim_controller.request_save()
    #     self._settings_side_bar.update_save_info()
    #     self._settings_side_bar.clear_disabled = False
    #     self._settings_side_bar.update_clear_info(f"{self._sim_controller.h5_size/1000000000:.1f}GB")

    @Slot()
    # def _on_clear_sim_requested(self):
    #     self._settings_side_bar.save_disabled = True
    #     self._sim_controller.request_clear()
    #     self._settings_side_bar.update_save_info()
    #     self._settings_side_bar.clear_disabled = True
    #     self._settings_side_bar.update_clear_info()

    def _update_image_type(self) -> None:
        """
        Updates the image type for the simulation controller based on the current state toggles.
        - Generated by OpenAI's GPT 5.5
        """
        velocity = self._settings_side_bar.velocity_state == 1
        density = self._settings_side_bar.density_state == 1
        stream = self._settings_side_bar.streamlines_state == 1
        curl = self._settings_side_bar.curl_state == 1

        if velocity:
            if stream: self._sim_controller.image_type = SimImageType.VELOCITY_HEAT_STREAM
            elif curl: self._sim_controller.image_type = SimImageType.VELOCITY_HEAT_CURL
            else: self._sim_controller.image_type = SimImageType.VELOCITY_HEAT
            return
        elif density:
            if stream: self._sim_controller.image_type = SimImageType.DENSITY_HEAT_STREAM
            elif curl: self._sim_controller.image_type = SimImageType.DENSITY_HEAT_CURL
            else: self._sim_controller.image_type = SimImageType.DENSITY_HEAT
        elif stream: self._sim_controller.image_type = SimImageType.STREAM
        elif curl: self._sim_controller.image_type = SimImageType.CURL
        else: self._sim_controller.image_type = SimImageType.NONE

    @Slot()
    def _on_play_pressed(self) -> None:
        """
        Handles the play button press event to start the simulation. - Generated by OpenAI's GPT 5.5
        """
        self._sim_controller.reset()
        self._settings_side_bar.sim_playing = True

        if not self._sim_thread.isRunning():
            self._sim_thread.start()

        if not self._title_bar.is_analysis_checked:
            self._title_bar.click_analysis()
        self._analysis_tab.set_results_tab_active()

        vertices = self._editor.get_vertices()
        self._simulation_engine.vertices = vertices

        data = [self.wind_speed, [self._editor.width(), self._editor.height()]]

        self._sim_controller.show()
        self.runSimulation.emit(data)

        width = self.window().width()
        height = self.window().height()
        self.window().setFixedSize(width, height)

    @Slot()
    def on_stop_pressed(self) -> None:
        """
        Handles the stop button press event to stop the simulation. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.sim_playing = False
        self._sim_controller.hide()
        self._state_manager.set_cursor_state(QStateManager.CursorState.DEFAULT)

        if self._sim_thread.isRunning():
            self._sim_thread.requestInterruption()
            self._sim_thread.quit()
            self._sim_thread.wait()

        self._sim_controller.reset()
        self._editor.display_pixmap()

        self.window().setMinimumWidth(self._minimum_window_width)
        self.window().setMinimumHeight(self._minimum_window_height)
        self.window().setMaximumWidth(self._maximum_window_width)
        self.window().setMaximumHeight(self._maximum_window_height)

        self._settings_side_bar.update_save_info()
        self._settings_side_bar.update_clear_info()
        self._settings_side_bar.save_disabled = True
        self._settings_side_bar.clear_disabled = True

        self._analysis_tab.simulation_progress = 0
        self._analysis_tab.set_sim_info_label(" - ")
        self._analysis_tab.set_drag_coef_value(" - ")
        self._analysis_tab.set_lift_coef_value(" - ")
        self._analysis_tab.set_reynolds_number_value(" - ")
        self._analysis_tab.set_mach_number_value(" - ")
        self._analysis_tab.set_kinetic_energy_value(" - ")
        self._analysis_tab.set_pressure_drop_value(" - ")
        self._analysis_tab.set_total_mass_value(" - ")
        self._analysis_tab.set_total_enstrophy_value(" - ")
        self._analysis_tab.set_max_vorticity_value(" - ")

    @Slot(int)
    def _on_sim_progressed(self, progress: int) -> None:
        """
        Handles simulation progress updates. - Generated by OpenAI's GPT 5.5
        """
        # print(f"Simulation progress: {progress}%")
        self._analysis_tab.simulation_progress = progress

    def resizeEvent(self, event) -> None:
        """
        Handles the resize event to adjust the size of certain UI elements dynamically. - Generated by OpenAI's GPT 5.5

        :param event: The resize event instance containing information about the
            resizing operation.
        :return: None
        """
        self._save_warning.setGeometry(0, 0, self.width(), self.height())
        self._save_warning_window.move(QPoint(self.width()//2 - self._save_warning_window.width()//2,
                                              self.height()//2 - self._save_warning_window.height()//2))
        self._sim_controller.canvas_height = self._editor.height()
        self._sim_controller.canvas_width = self._editor.width()

    @Slot()
    def _on_save_project(self, force_save_as: bool = False) -> None:
        """
        Handles the process of saving a project and emits the saved data.

        This method collects and modifies the current project data by assigning
        a description containing the current date. The updated data is then
        emitted via a signal for further processing. - Generated by OpenAI's GPT 5.5

        :return: None
        """
        saved_data = self._editor.save_data()

        today_date = date.today()
        project_description = str(today_date)

        saved_data["Project_description"] = project_description
        saved_data["Live_edit_state"] = self._settings_side_bar.live_edit_state
        saved_data["Velocity_state"] = self._settings_side_bar.velocity_state
        saved_data["Density_state"] = self._settings_side_bar.density_state
        saved_data["Streamlines_state"] = self._settings_side_bar.streamlines_state
        saved_data["Curl_state"] = self._settings_side_bar.curl_state
        saved_data["Streamline_count"] = self._settings_side_bar.streamline_count

        self.saveProject.emit(saved_data) if not force_save_as else self.saveAsProject.emit(saved_data)

    @Slot()
    def _on_save_as_project(self) -> None:
        self._on_save_project(force_save_as=True)

    def set_warning_visible(self, visible: bool) -> None:
        """
        Sets the visibility of the warning message and manages the state of the associated UI
        components, including enabling or disabling the title bar, showing or hiding the
        analysis tab, and clearing the "analysis checked" state if applicable. - Generated by OpenAI's GPT 5.5

        :param visible: Boolean indicating whether the warning should be visible.
        :type visible: bool
        :return: None
        """
        if visible:
            self._save_warning.show()
            self._save_warning.raise_()
            if self._title_bar.is_analysis_checked:
                self._title_bar.is_analysis_checked = False
                self._analysis_tab.hide()

            self._title_bar.setDisabled(True)
        else:
            self._save_warning.hide()
            self._title_bar.setDisabled(False)

    def load_editor_data(self, data: dict) -> None:
        """
        Loads data into the editor instance.

        This function is responsible for loading the provided data into the editor. It
        delegates the operation to the internal editor object, ensuring the data is
        parsed and handled as required. - Generated by OpenAI's GPT 5.5

        :param data: The data to be loaded into the editor.
        :type data: dict
        :return: None
        """
        self._editor.load_data(data)

    @Slot(bool)
    def _on_analysis_pressed(self, pressed: bool) -> None:
        """
        Handles the toggling of the analysis tab's visibility based on the `pressed` state.
        - Generated by OpenAI's GPT 5.5

        :param pressed: A boolean indicating whether the analysis tab should be shown
            or hidden. If True, the analysis tab will be shown, otherwise it will be hidden.
        :type pressed: bool
        """
        if pressed:
            self._analysis_tab.show()
            self._analysis_tab.raise_()
        else:
            self._analysis_tab.hide()

    @property
    def title_bar(self) -> QCustomTitleBar:
        """
        Gets the custom title bar instance associated with the current context. - Generated by OpenAI's GPT 5.5

        :return: The custom title bar associated with this instance.
        :rtype: QCustomTitleBar
        """
        return self._title_bar

    @property
    def constraint_method(self) -> str:
        """
        Gets the constraint method associated with the tool bar.

        This property retrieves the current constraint method value from the
        tool bar. The constraint method can be used to understand or modify
        how constraints are applied in a specific context. - Generated by OpenAI's GPT 5.5

        :return: The constraint method as a string.
        :rtype: str
        """
        return self._settings_side_bar.constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint: str) -> None:
        """
        Sets the constraint method for the tool bar. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.constraint_method = constraint

    @property
    def threshold(self) -> int:
        """
        Gets the current threshold value for the toolbar configuration.

        The threshold value determines the limit or boundary at which a specific
        action, calculation, or configuration applies within the toolbar logic. It
        is an important property meant for controlling user interface behavior
        or internal processes bound to the toolbar. - Generated by OpenAI's GPT 5.5

        :return: The integer value of the threshold.
        :rtype: int
        """
        return self._settings_side_bar.threshold
    @threshold.setter
    def threshold(self, threshold: int) -> None:
        """
        Sets the threshold for the tool bar. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.threshold = threshold

    @property
    def iterations(self) -> int:
        """
        Provides access to the number of iterations stored in the toolbar. - Generated by OpenAI's GPT 5.5

        :return: The number of iterations.
        :rtype: int
        """
        return self._settings_side_bar.iterations
    @iterations.setter
    def iterations(self, iterations: int) -> None:
        """
        Sets the number of iterations for the tool bar. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.iterations = iterations

    @property
    def quality(self) -> float:
        """
        Gets the quality value of the tool bar. - Generated by OpenAI's GPT 5.5

        :return: The quality value of type float.
        :rtype: float
        """
        return self._settings_side_bar.quality
    @quality.setter
    def quality(self, quality: float) -> None:
        """
        Sets the quality property of the toolbar. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.quality = quality

    @property
    def wind_speed(self) -> float:
        """
        Retrieves the wind speed value from the tool bar. - Generated by OpenAI's GPT 5.5

        :return: Wind speed value as a floating-point number.
        :rtype: float
        """
        return self._settings_side_bar.wind_speed
    @wind_speed.setter
    def wind_speed(self, wind_speed: float) -> None:
        """
        Sets the wind speed for the tool bar. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.wind_speed = wind_speed

    @property
    def viscosity(self) -> float:
        return self._settings_side_bar.viscosity

    @property
    def allocation(self) -> int:
        """
        Returns the memory allocation for the simulation. - Generated by OpenAI's GPT 5.5
        """
        return self._allocation

    @allocation.setter
    def allocation(self, allocation: int) -> None:
        """
        Sets the memory allocation and updates the simulation engine. - Generated by OpenAI's GPT 5.5
        """
        self._allocation = allocation
        self._simulation_engine.allocation = allocation

    @Slot(int)
    def set_allocation(self, allocation: int) -> None:
        """
        Slot to set the memory allocation. - Generated by OpenAI's GPT 5.5
        """
        self.allocation = allocation

    @property
    def viscosity(self) -> float:
        return self._settings_side_bar.viscosity
    @viscosity.setter
    def viscosity(self, viscosity: float) -> None:
        """
        Sets the viscosity in the settings. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.viscosity = viscosity

    #region States properties
    @property
    def live_edit_state(self) -> int:
        return self._settings_side_bar.live_edit_state
    @live_edit_state.setter
    def live_edit_state(self, state: int) -> None:
        """
        Sets the live edit state. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.live_edit_state = state
        self._update_image_type()

    @property
    def velocity_state(self) -> int:
        """
        Returns the velocity state toggle value. - Generated by OpenAI's GPT 5.5
        """
        return self._settings_side_bar.velocity_state
    @velocity_state.setter
    def velocity_state(self, state: int) -> None:
        """
        Sets the velocity state toggle value.
        """
        self._settings_side_bar.velocity_state = state
        self._update_image_type()

    @property
    def density_state(self) -> int:
        """
        Returns the density state toggle value. - Generated by OpenAI's GPT 5.5
        """
        return self._settings_side_bar.density_state
    @density_state.setter
    def density_state(self, state: int) -> None:
        """
        Sets the density state toggle value. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.density_state = state
        self._update_image_type()

    @property
    def streamlines_state(self) -> int:
        """
        Returns the streamlines state toggle value. - Generated by OpenAI's GPT 5.5
        """
        return self._settings_side_bar.streamlines_state
    @streamlines_state.setter
    def streamlines_state(self, state: int) -> None:
        """
        Sets the streamlines state toggle value. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.streamlines_state = state
        self._update_image_type()

    @property
    def curl_state(self) -> int:
        """
        Returns the curl state toggle value. - Generated by OpenAI's GPT 5.5
        """
        return self._settings_side_bar.curl_state
    @curl_state.setter
    def curl_state(self, state: int) -> None:
        """
        Sets the curl state toggle value. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.curl_state = state
        self._update_image_type()
    #endregion

    @property
    def streamline_count(self) -> int:
        return self._settings_side_bar.streamline_count
    @streamline_count.setter
    def streamline_count(self, count: int) -> None:
        """
        Sets the streamline count. - Generated by OpenAI's GPT 5.5
        """
        self._settings_side_bar.streamline_count = count

    def on_page_quit(self) -> None:
        """
        Handles cleanup when the page is closed. - Generated by OpenAI's GPT 5.5
        """
        if self._title_bar.is_analysis_checked:
            self._title_bar.click_analysis()

        self._title_bar.analysisPressed.disconnect()