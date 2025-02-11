from PySide6.QtCore import QObject, Signal, Slot, Property, QThread
from backend.chatbot_handler import ChatbotHandler
import threading

class ChatWorker(QThread):
    responseReceived = Signal(str)
    responseComplete = Signal()
    
    def __init__(self, chatbot_handler, message):
        super().__init__()
        self.chatbot_handler = chatbot_handler
        self.message = message
        
    def run(self):
        try:
            self.chatbot_handler.handle_user_input(self.message)
        except Exception as e:
            self.responseReceived.emit(f"[Error: {str(e)}]")
            self.responseComplete.emit()

class DummyAnimationManager:
    def __init__(self):
        self.current_face_state = "IDLE"
        
    def set_face_state(self, state):
        self.current_face_state = state
        
    def stop_all_animations(self):
        self.current_face_state = "IDLE"

class ChatController(QObject):
    messageReceived = Signal(str, str)  # message, type (user/ai)
    messageUpdated = Signal(int, str)  # message_id, new_text
    thinkingStateChanged = Signal(bool)
    errorOccurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_chatbot()
        self._current_worker = None
        self._is_thinking = False
        self._current_response = ""
        self._current_message_id = None
        self._message_counter = 0
        
    def _setup_chatbot(self):
        class QtEventManager:
            def __init__(self, controller):
                self.controller = controller
                self.subscribers = {}
                
            def subscribe(self, event_type, handler):
                if event_type not in self.subscribers:
                    self.subscribers[event_type] = []
                self.subscribers[event_type].append(handler)
                
            def publish(self, event_type, data=None):
                if event_type == "DISPLAY_USER_MESSAGE":
                    self.controller._message_counter += 1
                    self.controller.messageReceived.emit("You: " + data, "user")
                elif event_type == "AI_THINKING_START":
                    self.controller._is_thinking = True
                    self.controller._current_response = ""
                    self.controller.thinkingStateChanged.emit(True)
                    self.controller._message_counter += 1
                    self.controller._current_message_id = self.controller._message_counter
                    self.controller.messageReceived.emit(
                        f"{self.controller.chatbot.ai_name}: ", "ai"
                    )
                elif event_type == "AI_RESPONSE_CHUNK":
                    self.controller._current_response += data
                    if self.controller._current_message_id is not None:
                        self.controller.messageUpdated.emit(
                            self.controller._current_message_id,
                            f"{self.controller.chatbot.ai_name}: {self.controller._current_response}"
                        )
                elif event_type == "AI_RESPONSE_COMPLETE":
                    if self.controller._current_message_id is not None:
                        self.controller.messageUpdated.emit(
                            self.controller._current_message_id,
                            f"{self.controller.chatbot.ai_name}: {self.controller._current_response}"
                        )
                    self.controller._current_response = ""
                    self.controller._current_message_id = None
                    self.controller._is_thinking = False
                    self.controller.thinkingStateChanged.emit(False)
        
        self.event_manager = QtEventManager(self)
        self.animation_manager = DummyAnimationManager()
        self.chatbot = ChatbotHandler(
            event_manager=self.event_manager,
            animation_manager=self.animation_manager
        )
    
    @Property(bool, notify=thinkingStateChanged)
    def isThinking(self):
        return self._is_thinking
    
    @Slot(str)
    def sendMessage(self, message: str):
        """Send a message to the chatbot"""
        if self._is_thinking:
            self.errorOccurred.emit("Still processing previous message")
            return
            
        if not message.strip():
            return
            
        # Create and start worker thread for processing
        self._current_worker = ChatWorker(self.chatbot, message)
        self._current_worker.start()
        
    @Slot(str)
    def switchPersonality(self, personality: str):
        """Switch the chatbot personality"""
        # If we're in the middle of a response, cancel it
        if self._is_thinking:
            if self._current_worker and self._current_worker.isRunning():
                self._current_worker.terminate()
                self._current_worker.wait()
            self._is_thinking = False
            self.thinkingStateChanged.emit(False)
        
        # Reset state
        self._current_response = ""
        self._current_message_id = None
        
        # Switch personality
        if self.chatbot.switch_personality(personality):
            self._message_counter += 1
            self.messageReceived.emit(
                f"Switched to {personality} personality",
                "system"
            )
        else:
            self.errorOccurred.emit(f"Failed to switch to {personality} personality")
            
    def cleanup(self):
        """Clean up resources before shutdown"""
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.terminate()
            self._current_worker.wait()
        if hasattr(self, 'chatbot'):
            self.chatbot._stop_current_model()