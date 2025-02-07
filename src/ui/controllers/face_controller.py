from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from backend.ASCII_Face import FRAMES_BY_STATE

class FaceController(QObject):
    stateChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state = "WELCOME"
        self._frames_by_state = FRAMES_BY_STATE
        self.state_timers = {}
        
    @Property(str, notify=stateChanged)
    def currentState(self):
        return self._current_state
        
    @Slot(str)
    def setState(self, state, duration=None):
        if state in self._frames_by_state:
            self._current_state = state
            self.stateChanged.emit(state)
            
            # Cancel any pending state changes
            for timer in self.state_timers.values():
                timer.stop()
            
            # If duration specified, schedule next state change
            if duration is not None:
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: self.setState("IDLE"))
                timer.start(duration)
                self.state_timers[state] = timer
            
    @Slot(str, result='QVariantList')
    def getFramesForState(self, state):
        return self._frames_by_state.get(state, [])

    @Slot()
    def switchToIdle(self):
        self.setState("IDLE")