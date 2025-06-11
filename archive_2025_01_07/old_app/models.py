#!/usr/bin/env python3
"""
Упрощённые модели данных для Universal Agent Platform

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только необходимые модели
- Минимум полей
- Простая структура
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class ChannelMapping(BaseModel):
    """
    Простой маппинг канала на сценарий.
    
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
    Заменяет сложную модель Agent простой таблицей соответствий.
    """
    id: Optional[str] = Field(None, description="MongoDB ObjectId маппинга")
    channel_id: str = Field(description="ID канала (agent_id, chat_id, etc)")
    scenario_id: str = Field(description="ID сценария для выполнения")
    channel_type: str = Field(description="Тип канала: telegram, console, api")
    
    # Конфигурация канала (токены, настройки и т.д.)
    channel_config: Dict[str, Any] = Field(default_factory=dict, description="Конфигурация канала")
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }





class Scenario(BaseModel):
    """Упрощённая модель сценария"""
    id: Optional[str] = Field(None, description="MongoDB ObjectId сценария")
    scenario_id: str = Field(description="Уникальный ID сценария")
    name: str = Field(description="Название сценария")
    description: Optional[str] = Field(None, description="Описание сценария")
    
    # Структура сценария
    steps: List[Dict[str, Any]] = Field(description="Шаги сценария")
    initial_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Метаданные
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = Field(default=0)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    """Упрощённая модель пользователя"""
    id: Optional[str] = Field(None, description="MongoDB ObjectId пользователя")
    user_id: str = Field(description="ID пользователя в канале")
    channel_type: str = Field(description="Тип канала")
    user_name: Optional[str] = Field(None, description="Имя пользователя")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    
    # Метаданные
    first_interaction: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    
    # Персонализация
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ScenarioExecution(BaseModel):
    """Упрощённая модель выполнения сценария"""
    id: Optional[str] = Field(None, description="MongoDB ObjectId выполнения")
    agent_id: str = Field(description="ID агента")
    scenario_id: str = Field(description="ID сценария")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    chat_id: Optional[str] = Field(None, description="ID чата")
    
    # Результат выполнения
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = Field(None)
    is_successful: Optional[bool] = Field(None)
    error_message: Optional[str] = Field(None)
    
    # Контекст
    initial_context: Dict[str, Any] = Field(default_factory=dict)
    final_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Шаги выполнения
    executed_steps: List[str] = Field(default_factory=list)
    current_step: Optional[str] = Field(None)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 