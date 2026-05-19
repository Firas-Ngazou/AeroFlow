from PySide6.QtCore import Qt, Slot, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLabel, QComboBox, QScrollArea

from dev.user_interface.components.q_buttons import QSettingsTabPB
from dev.user_interface.groups.q_slider_groups import QSliderGroup, QRealSliderGroup
from dev.user_interface.groups.q_checkboxes import QDoubleCheckBox, QInfoCheckbox
from dev.user_interface.groups.q_save_clear import QSaveClear


class QSettingsGeneralTab(QWidget):
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
    saveRequested = Signal()
    clearRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._sim_playing = False

        # Resolution
        self._quality = QRealSliderGroup("QUALITY")

        self._quality.minimum = 0.1
        self._quality.maximum = 1.0
        self._quality.single_step = 0.01
        self._quality.default_value = 1.0

        high_res_warning = QLabel(" ATTENTION : Une trop haute valeur peut résulter \n"
                                  " en une perte de performance importante.")
        high_res_warning.setFont(QFont("JetBrains Mono", 8))

        # Wind speed
        self._wind_speed = QRealSliderGroup("VITESSE (m/s)")
        self._wind_speed.minimum = 1.0
        self._wind_speed.maximum = 100.0

        # Viscosity
        self._viscosity = QRealSliderGroup("VISCOSITÉ")
        self._viscosity.decimals = 4
        self._viscosity.minimum = 0.0040
        self._viscosity.maximum = 10.0
        self._viscosity.single_step = 0.005
        self._viscosity.default_value = 0.005

        # Live-edit
        self._live_edit = QInfoCheckbox("LIVE-EDIT",
                                        """
                                        <div style="text-align: left;">
                                            <p>Lorsque sélectionné, cette option rend possible
                                            l'édition en temps réel du dessin vectoriel.
                                        
                                            <p>Il ne sera pas possible de manipuler le controlleur vidéo, ni de 
                                            sauvegarder la simulation pour pouvoir la visualiser plus rapidement la 
                                            prochaine fois.
                                        
                                            <p>Les calculs sont effectués en temps réelle, ce qui pourrait expliquer 
                                            unecertaine perte en performances.
                                        </div>
                                        """)

        # Check boxes
        self._heatmaps_cb = QDoubleCheckBox("HEATMAPS", "VÉLOCITÉ", "DENSITÉ")
        self._other_cb = QDoubleCheckBox("AUTRE", "ÉCOULEMENT", "TOURBILLONS")

        # Streamline count
        self._streamline_count = QSliderGroup("ÉCOULEMENT")
        self._streamline_count.minimum = 5
        self._streamline_count.maximum = 80
        self._streamline_count.single_step = 5
        self._streamline_count.default_value = 20

        # Save/Clear buttons
        # self._save_clear = QSaveClear()

        self._staircase_cb = QInfoCheckbox("CACHER L'EFFET ESCALIER",
                                           """
                                           <div style="text-align: left;">
                                                <p>Afin de donner à la visualisation une fluidité minimale, 
                                                la simulation est effectuée à une résolution réduite.
                                                
                                                <p>Cela à pour effet de laisser apparaître un effet d'escalier autour
                                                des objets vectoriels déssinés.
                                                
                                                <p>Lorsque l'option est activée, l'effet d'escalier est caché en dessous 
                                                des objets vectoriels au prix de devoir réduire la précision et la 
                                                taille exacte des objets, ce qui peut résulter en un mouvement de 
                                                fluide imprécis.
                                                
                                                <p>Lorsque l'option est désactivée, l'effet d'escalier est visible 
                                                autour des objets vectoriels déssinés, mais la taille exacte des objets
                                                est maintenue.
                                           </div>
                                           """)

        # Layouts
        content_widget = QWidget()
        content_widget.setFixedWidth(345)
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(self._quality)
        content_layout.addWidget(high_res_warning)
        content_layout.addSpacing(20)
        content_layout.addWidget(self._wind_speed)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._viscosity)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._live_edit)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._heatmaps_cb)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._other_cb)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._streamline_count)
        content_layout.addSpacing(10)
        content_layout.addWidget(self._staircase_cb)
        # content_layout.addWidget(self._save_clear)

        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(content_widget)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll_area)

        # Connections
        self._quality.realValueChanged.connect(self.qualityChanged.emit)
        self._wind_speed.realValueChanged.connect(self.windSpeedChanged.emit)
        self._viscosity.realValueChanged.connect(self.viscosityChanged.emit)
        self._live_edit.stateChanged.connect(self.liveEditStateChanged.emit)
        self._heatmaps_cb.leftStateChanged.connect(self.velocityStateChanged.emit)
        self._heatmaps_cb.rightStateChanged.connect(self.densityStateChanged.emit)
        self._other_cb.leftStateChanged.connect(self.streamlinesStateChanged.emit)
        self._other_cb.rightStateChanged.connect(self.curlStateChanged.emit)
        self._streamline_count.valueChanged.connect(self.streamlineCountChanged.emit)
        self._staircase_cb.stateChanged.connect(self.staircaseStateChanged.emit)
        # self._save_clear.saveRequested.connect(self.saveRequested.emit)
        # self._save_clear.clearRequested.connect(self.clearRequested.emit)

    @property
    def quality(self) -> float:
        return self._quality.value
    @quality.setter
    def quality(self, value: float):
        self._quality.value = value

    @property
    def wind_speed(self) -> float:
        return self._wind_speed.value
    @wind_speed.setter
    def wind_speed(self, value: float):
        self._wind_speed.value = value

    @property
    def viscosity(self) -> float:
        return self._viscosity.value
    @viscosity.setter
    def viscosity(self, value: float) -> None:
        self._viscosity.value = value

    @property
    def live_edit_state(self) -> int:
        return self._live_edit.state
    @live_edit_state.setter
    def live_edit_state(self, state: int) -> None:
        self._live_edit.state = state

    @property
    def velocity_state(self) -> int:
        return self._heatmaps_cb.left_state
    @velocity_state.setter
    def velocity_state(self, state: int) -> None:
        self._heatmaps_cb.left_state = state

    @property
    def density_state(self) -> int:
        return self._heatmaps_cb.right_state
    @density_state.setter
    def density_state(self, state: int) -> None:
        self._heatmaps_cb.right_state = state

    @property
    def streamlines_state(self) -> int:
        return self._other_cb.left_state
    @streamlines_state.setter
    def streamlines_state(self, state: int) -> None:
        self._other_cb.left_state = state

    @property
    def curl_state(self) -> int:
        return self._other_cb.right_state
    @curl_state.setter
    def curl_state(self, state: int) -> None:
        self._other_cb.right_state = state

    @property
    def staircase_state(self) -> int:
        return self._staircase_cb.state
    @staircase_state.setter
    def staircase_state(self, state: int) -> None:
        self._staircase_cb.state = state

    @property
    def streamline_count(self) -> int:
        return self._streamline_count.value
    @streamline_count.setter
    def streamline_count(self, value: int):
        self._streamline_count.value = value

    @property
    def sim_playing(self) -> bool:
        return self._sim_playing
    @sim_playing.setter
    def sim_playing(self, value: bool):
        self._wind_speed.setDisabled(value)
        self._live_edit.setDisabled(value)
        self._viscosity.setDisabled(value)
        self._staircase_cb.setDisabled(value)
        self._sim_playing = value

    # @property
    # def save_disabled(self) -> bool:
    #     return self._save_clear.save_disabled
    # @save_disabled.setter
    # def save_disabled(self, state: bool):
    #     self._save_clear.save_disabled = state

    # @property
    # def clear_disabled(self) -> bool:
    #     return self._save_clear.clear_disabled
    # @clear_disabled.setter
    # def clear_disabled(self, state: bool):
    #     self._save_clear.clear_disabled = state

    # @property
    # def save_info(self) -> str:
    #     return self._save_clear.save_info
    # @save_info.setter
    # def save_info(self, info: str):
    #     self._save_clear.save_info = info

    # @property
    # def clear_info(self) -> str:
    #     return self._save_clear.clear_info
    # @clear_info.setter
    # def clear_info(self, info: str):
    #     self._save_clear.clear_info = info

class QSettingsOptimizationTab(QWidget):
    constraintChanged = Signal(str)
    iterationsChanged = Signal(int)
    thresholdChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._sim_playing = False

        # Constraint method
        # Title
        self._title = QLabel("CONTRAINTE")
        self._title.setFont(QFont("JetBrains Mono", 11))

        # Combobox
        self._combo_box = QComboBox()
        self._combo_box.setPlaceholderText("MÉTHODE")
        self._combo_box.setProperty("class", "settings_combo_box")
        self._combo_box.setFixedSize(150, 30)
        self._combo_box.setFont(QFont("JetBrains Mono", 9))

        self._combo_box.addItem("DISTANCE")
        self._combo_box.addItem("SURFACE")

        self._combo_box.setCurrentIndex(1)

        # Primary frame & layout
        constraint_frame = QFrame()
        constraint_frame.setProperty("class", "constraint_frame")
        self._constraint_layout = QHBoxLayout(constraint_frame)

        self._constraint_layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignLeft)
        self._constraint_layout.addWidget(self._combo_box, alignment=Qt.AlignmentFlag.AlignRight)
        self._constraint_layout.setContentsMargins(15, 0, 0, 0)

        # Threshold
        self._threshold_setting = QSliderGroup("SEUIL (%)")
        self._threshold_setting.minimum = 1
        self._threshold_setting.maximum = 100
        self._threshold_setting.single_step = 5
        self._threshold_setting.default_value = 5

        # Iterations
        self._iterations_setting = QSliderGroup("ITÉRATIONS")
        self._iterations_setting.minimum = 1
        self._iterations_setting.maximum = 1000
        self._iterations_setting.single_step = 5
        self._iterations_setting.default_value = 20

        # Root
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(constraint_frame)
        root_layout.addWidget(self._threshold_setting)
        root_layout.addWidget(self._iterations_setting)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addStretch()

        # Connections
        self._combo_box.currentTextChanged.connect(self.constraintChanged.emit)
        self._threshold_setting.valueChanged.connect(self.thresholdChanged.emit)
        self._iterations_setting.valueChanged.connect(self.iterationsChanged.emit)

    @property
    def constraint_method(self) -> str:
        return self._combo_box.currentText()
    @constraint_method.setter
    def constraint_method(self, constraint: str) -> None:
        self._combo_box.setCurrentText(constraint)

    @property
    def threshold(self) -> int:
        return self._threshold_setting.value
    @threshold.setter
    def threshold(self, threshold: int) -> None:
        self._threshold_setting.set_value(threshold)

    @property
    def iterations(self) -> int:
        return self._iterations_setting.value
    @iterations.setter
    def iterations(self, iterations: int) -> None:
        self._iterations_setting.set_value(iterations)

    @property
    def sim_playing(self) -> bool:
        return self._sim_playing
    @sim_playing.setter
    def sim_playing(self, value: bool) -> None:
        self._iterations_setting.setDisabled(value)
        self._combo_box.setDisabled(value)
        self._threshold_setting.setDisabled(value)
        self._sim_playing = value

class QSettingsSideBar(QWidget):
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
    saveRequested = Signal()
    clearRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Setup
        self._current_tab = 0

        self._height = 800
        self._primary_frame = QFrame()
        self._primary_frame.setProperty("class", "primary_frame")

        self._full_frame = QFrame()
        self._full_frame.setFixedHeight(self._height)

        self._side_button_layout = QHBoxLayout(self._full_frame)

        self._primary_layout = QVBoxLayout(self._primary_frame)
        self._primary_layout.setContentsMargins(10, 10, 10, 5)

        self._secondary_layout = QHBoxLayout()
        self._secondary_layout.setContentsMargins(10, 5, 10, 5)
        self._primary_layout.addLayout(self._secondary_layout)

        self._collapsed_width = 25
        self._expanded_width = 400

        self._full_frame.setMaximumWidth(self._collapsed_width)

        self._is_collapsed = True
        self._sim_playing = False

        # Side button
        self._open_icon = QIcon(":/res/left_arrow_icon_black.png")
        self._close_icon = QIcon(":/res/right_arrow_icon_black.png")
        self._side_button = QPushButton()
        self._side_button.setIcon(self._open_icon)
        self._side_button.setProperty("class", "sidebar_pb")
        self._side_button.setFixedSize(25, self._height - 200)
        self._side_button_layout.setContentsMargins(2, 0, 0, 0)
        self._side_button_layout.addWidget(self._side_button,
                                           alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._side_button_layout.addWidget(self._primary_frame)

        # General tab
        self._general_button = QSettingsTabPB("GÉNÉRAL")
        self._general_button.setChecked(True)
        self._secondary_layout.addWidget(self._general_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                   Qt.AlignmentFlag.AlignLeft)
        self._general_tab = QSettingsGeneralTab()
        self._primary_layout.addWidget(self._general_tab)

        # Optimization tab
        self._optimization_button = QSettingsTabPB("OPTIMIZATION")
        self._secondary_layout.addWidget(self._optimization_button, alignment=Qt.AlignmentFlag.AlignTop |
                                                                        Qt.AlignmentFlag.AlignRight)
        self._optimization_tab = QSettingsOptimizationTab()
        self._primary_layout.addWidget(self._optimization_tab)
        self._optimization_tab.hide()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self._full_frame)

        # Connections
        self._general_button.clicked.connect(self._on_tab_changed)
        self._optimization_button.clicked.connect(self._on_tab_changed)

        self._general_tab.qualityChanged.connect(self.qualityChanged.emit)
        self._general_tab.windSpeedChanged.connect(self.windSpeedChanged.emit)
        self._general_tab.viscosityChanged.connect(self.viscosityChanged.emit)
        self._general_tab.liveEditStateChanged.connect(self.liveEditStateChanged.emit)
        self._general_tab.velocityStateChanged.connect(self.velocityStateChanged.emit)
        self._general_tab.densityStateChanged.connect(self.densityStateChanged.emit)
        self._general_tab.streamlinesStateChanged.connect(self.streamlinesStateChanged.emit)
        self._general_tab.curlStateChanged.connect(self.curlStateChanged.emit)
        self._general_tab.streamlineCountChanged.connect(self.streamlineCountChanged.emit)
        self._general_tab.staircaseStateChanged.connect(self.staircaseStateChanged.emit)
        self._general_tab.saveRequested.connect(self.saveRequested.emit)
        self._general_tab.clearRequested.connect(self.clearRequested.emit)

        self._optimization_tab.constraintChanged.connect(self.constraintChanged.emit)
        self._optimization_tab.iterationsChanged.connect(self.iterationsChanged.emit)
        self._optimization_tab.thresholdChanged.connect(self.thresholdChanged.emit)

        self._side_button.pressed.connect(self._on_side_button_pressed)

        # Animation
        self._animation = QPropertyAnimation(self._full_frame, b"maximumWidth")
        self._animation.setDuration(400)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_animation_finished)

        self.is_collapsed = True

    def resizeEvent(self, event):
        self._height = self.window().height() - 300
        self._side_button.setFixedHeight(self._height)
        self._full_frame.setFixedHeight(self._height)

    @property
    def constraint_method(self) -> str:
        return self._optimization_tab.constraint_method
    @constraint_method.setter
    def constraint_method(self, constraint: str) -> None:
        self._optimization_tab.constraint_method = constraint

    @property
    def threshold(self) -> int:
        return self._optimization_tab.threshold
    @threshold.setter
    def threshold(self, threshold: int) -> None:
        self._optimization_tab.threshold = threshold

    @property
    def iterations(self) -> int:
        return self._optimization_tab.iterations
    @iterations.setter
    def iterations(self, iterations: int) -> None:
        self._optimization_tab.iterations = iterations

    @property
    def quality(self) -> float:
        return self._general_tab.quality
    @quality.setter
    def quality(self, quality: float):
        self._general_tab.quality = quality

    @property
    def wind_speed(self) -> float:
        return self._general_tab.wind_speed
    @wind_speed.setter
    def wind_speed(self, wind_speed: float):
        self._general_tab.wind_speed = wind_speed

    @property
    def viscosity(self) -> float:
        return self._general_tab.viscosity
    @viscosity.setter
    def viscosity(self, viscosity: float) -> None:
        self._general_tab.viscosity = viscosity

    @property
    def live_edit_state(self) -> int:
        return self._general_tab.live_edit_state
    @live_edit_state.setter
    def live_edit_state(self, state: int) -> None:
        self._general_tab.live_edit_state = state

    @property
    def velocity_state(self) -> int:
        return self._general_tab.velocity_state
    @velocity_state.setter
    def velocity_state(self, state: int) -> None:
        self._general_tab.velocity_state = state

    @property
    def density_state(self) -> int:
        return self._general_tab.density_state
    @density_state.setter
    def density_state(self, state: int) -> None:
        self._general_tab.density_state = state

    @property
    def streamlines_state(self) -> int:
        return self._general_tab.streamlines_state
    @streamlines_state.setter
    def streamlines_state(self, state: int) -> None:
        self._general_tab.streamlines_state = state

    @property
    def curl_state(self) -> int:
        return self._general_tab.curl_state
    @curl_state.setter
    def curl_state(self, state: int) -> None:
        self._general_tab.curl_state = state

    @property
    def staircase_state(self) -> int:
        return self._general_tab.staircase_state
    @staircase_state.setter
    def staircase_state(self, state: int) -> None:
        self._general_tab.staircase_state = state

    @property
    def streamline_count(self) -> int:
        return self._general_tab.streamline_count
    @streamline_count.setter
    def streamline_count(self, count: int):
        self._general_tab.streamline_count = count

    @property
    def save_disabled(self) -> bool:
        return self._general_tab.save_disabled
    @save_disabled.setter
    def save_disabled(self, state: bool):
        self._general_tab.save_disabled = state

    @property
    def clear_disabled(self) -> bool:
        return self._general_tab.clear_disabled
    @clear_disabled.setter
    def clear_disabled(self, state: bool):
        self._general_tab.clear_disabled = state

    def update_save_info(self, info: str = " - "):
        self._general_tab.save_info = info

    def update_clear_info(self, info: str = " - "):
        self._general_tab.clear_info = info

    @Slot()
    def _on_tab_changed(self):
        sender = self.sender()

        # General tab was pressed
        if sender == self._general_button:

            # General tab was already pressed
            if self._current_tab == 0:
                self._general_button.setChecked(True)
                return

            # General tab was not pressed
            self._general_button.setChecked(True)
            self._optimization_button.setChecked(False)
            self._current_tab = 0
            self._optimization_tab.hide()
            self._general_tab.show()

        # Optimization tab was pressed
        else:

            # Optimization tab was already pressed
            if self._current_tab == 1:
                self._optimization_button.setChecked(True)

            # Optimization tab was not pressed
            self._optimization_button.setChecked(True)
            self._general_button.setChecked(False)
            self._current_tab = 1
            self._general_tab.hide()
            self._optimization_tab.show()

    @Slot()
    def _on_side_button_pressed(self):
        if self.is_collapsed:
            self.is_collapsed = False
        else:
            self.is_collapsed = True

    @property
    def is_collapsed(self) -> bool:
        return self._is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, value: bool):
        self._is_collapsed = value
        self._primary_frame.show()
        if self._is_collapsed:
            self._side_button.setIcon(self._open_icon)
            self._animation.setStartValue(self._expanded_width)
            self._animation.setEndValue(self._collapsed_width)
        else:
            self._side_button.setIcon(self._close_icon)
            self._animation.setStartValue(self._collapsed_width)
            self._animation.setEndValue(self._expanded_width)

        self._animation.start()

    @Slot()
    def _on_animation_finished(self):
        if self._is_collapsed:
            self._primary_frame.hide()

    @property
    def sim_playing(self):
        return self._sim_playing
    @sim_playing.setter
    def sim_playing(self, value: bool):
        self._general_tab.sim_playing = value
        self._optimization_tab.sim_playing = value
        self._sim_playing = value