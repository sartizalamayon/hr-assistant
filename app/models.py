import enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import EMBEDDING_DIM
from app.database import Base


class Role(str, enum.Enum):
    employee = "employee"
    hr = "hr"


class QuestionStatus(str, enum.Enum):
    answered_by_ai = "answered_by_ai"
    pending = "pending"
    resolved_by_hr = "resolved_by_hr"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    storage_path = Column(String, nullable=False)

    uploader = relationship("User")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
    chunk_index = Column(Integer, nullable=False)

    document = relationship("Document", back_populates="chunks")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    asked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    asked_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(QuestionStatus), nullable=False, default=QuestionStatus.pending)
    ai_answer = Column(Text, nullable=True)
    sources = Column(Text, nullable=True)  # comma-separated source document filenames
    hr_answer = Column(Text, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    asker = relationship("User", foreign_keys=[asked_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
