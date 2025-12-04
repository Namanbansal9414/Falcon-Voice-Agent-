# services/conversation_manager.py
import uuid
from typing import Dict, List, Literal, TypedDict

Role = Literal["user", "assistant"]
Mode = Literal["assistant", "coach", "support", "invest"]


class Message(TypedDict):
    role: Role
    content: str


class ConversationManager:
    """
    In-memory conversation store (perfect for demo/hackathon).
    """

    def __init__(self):
        # session_id -> {"mode": Mode, "messages": List[Message]}
        self.sessions: Dict[str, Dict[str, object]] = {}

    def create_session(self, mode: Mode = "assistant") -> str:
        sid = str(uuid.uuid4())
        self.sessions[sid] = {
            "mode": mode,
            "messages": [],
        }
        return sid

    def set_mode(self, session_id: str, mode: Mode):
        if session_id in self.sessions:
            self.sessions[session_id]["mode"] = mode

    def get_mode(self, session_id: str) -> Mode:
        session = self.sessions.get(session_id)
        if not session:
            return "assistant"
        return session.get("mode", "assistant")  # type: ignore

    def add_turn(self, session_id: str, user_text: str, assistant_text: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {"mode": "assistant", "messages": []}

        msgs: List[Message] = self.sessions[session_id]["messages"]  # type: ignore
        msgs.append({"role": "user", "content": user_text})
        msgs.append({"role": "assistant", "content": assistant_text})

    def get_history(self, session_id: str, max_messages: int = 10) -> List[Message]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        msgs: List[Message] = session["messages"]  # type: ignore
        return msgs[-max_messages:]
