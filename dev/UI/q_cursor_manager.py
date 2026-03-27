from PySide6.QtCore import QObject, Signal, Slot

from q_editor import StateManager


class QCursorManager(QObject):
    cursorStateChanged = Signal(int)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.__cursor_state = StateManager.CursorState.DEFAULT

    def set_cursor_state(self, state: int):
        self.cursor_state = StateManager.CursorState(state)
        self.cursorStateChanged.emit(state)

    @property
    def cursor_state(self) -> StateManager.CursorState:
        return self.__cursor_state

    @cursor_state.setter
    def cursor_state(self, state: StateManager.CursorState):
        self.__cursor_state = state