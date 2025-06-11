from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Template(Base):
    """Модель шаблона документа"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(Text, nullable=True)  # JSON строка переменных
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    owner = relationship("User", back_populates="templates")
    documents = relationship("Document", back_populates="template")

class Document(Base):
    """Модель сгенерированного документа"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    data_used = Column(Text, nullable=True)  # JSON строка использованных данных
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    template = relationship("Template", back_populates="documents")
    owner = relationship("User", back_populates="documents")