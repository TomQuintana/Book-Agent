"""Conversation service: metadata + message history backed by the database."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from src.helpers.create_title import generate_title

from ..database.models import Conversation, Message


class ConversationService:
    """CRUD for conversations and their messages over an injected session."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, thread_id: str, user_id: str = "default_user") -> Conversation:
        """Create and persist a new conversation (title starts as None)."""
        conv = Conversation(thread_id=thread_id, user_id=user_id)
        self.session.add(conv)
        self.session.commit()
        self.session.refresh(conv)
        return conv

    def get(self, thread_id: str) -> Conversation | None:
        """Fetch a conversation by thread_id, or None if it doesn't exist."""
        return self.session.get(Conversation, thread_id)

    def list(self, user_id: str | None = None) -> list[Conversation]:
        """List conversations, newest first, optionally filtered by user_id."""
        query = select(Conversation)
        if user_id:
            query = query.where(Conversation.user_id == user_id)
        query = query.order_by(Conversation.updated_at.desc())
        return self.session.exec(query).all()

    def add_message(self, thread_id: str, role: str, content: str) -> Message:
        """Append a message and touch the conversation's updated_at."""
        msg = Message(thread_id=thread_id, role=role, content=content)
        self.session.add(msg)
        conv = self.session.get(Conversation, thread_id)

        if conv:
            conv.updated_at = datetime.now()
            self.session.add(conv)

        self.session.commit()
        self.session.refresh(msg)

        return msg

    def get_messages(self, thread_id: str) -> list[Message]:
        """Return a conversation's messages ordered by creation time."""
        query = select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at)
        return self.session.exec(query).all()

    def set_title(self, thread_id: str, title: str) -> Conversation | None:
        """Set the conversation title, or return None if it doesn't exist."""
        conv = self.session.get(Conversation, thread_id)
        if not conv:
            return None
        conv.title = title
        self.session.add(conv)
        self.session.commit()
        self.session.refresh(conv)
        return conv

    def persist_turn(self, thread_id: str, user_message: str, response: str) -> None:
        """Saves the user/assistant pair of a successful turn, titling the conversation if new."""
        conversation = self.get(thread_id) or self.create(thread_id)

        if conversation is None:
            conversation = Conversation(thread_id=thread_id)
            self.session.add(conversation)

        self.session.add_all(
            [
                Message(thread_id=thread_id, role="user", content=user_message),
                Message(thread_id=thread_id, role="assistant", content=response),
            ]
        )

        conversation.updated_at = datetime.now()

        if conversation.title is None:
            conversation.title = generate_title(user_message)

        self.session.commit()
