"""
KittyCore 3.0 WebSocket Manager

Управление WebSocket соединениями для real-time коммуникации
с агентными системами.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Менеджер WebSocket соединений для KittyCore"""
    
    def __init__(self):
        # Активные соединения
        self.active_connections: Set[WebSocket] = set()
        
        # Соединения по комнатам/каналам (для группировки)
        self.rooms: Dict[str, Set[WebSocket]] = {}
        
        # Метаданные соединений
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Счетчик соединений
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket, room: str = "default") -> bool:
        """
        Подключить новый WebSocket
        
        Args:
            websocket: WebSocket соединение
            room: Комната/канал для группировки
            
        Returns:
            bool: Успешность подключения
        """
        try:
            await websocket.accept()
            
            # Добавляем в активные соединения
            self.active_connections.add(websocket)
            
            # Добавляем в комнату
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(websocket)
            
            # Сохраняем метаданные
            self.connection_metadata[websocket] = {
                "room": room,
                "connected_at": datetime.now(),
                "client_info": getattr(websocket, "client", None)
            }
            
            self.connection_count += 1
            
            logger.info(f"WebSocket connected to room '{room}'. Total connections: {len(self.active_connections)}")
            
            # Отправляем приветственное сообщение
            await self.send_personal_message(websocket, {
                "type": "connection_established",
                "room": room,
                "timestamp": datetime.now().isoformat(),
                "connection_id": id(websocket)
            })
            
            # Уведомляем остальных в комнате о новом подключении
            await self.broadcast_to_room(room, {
                "type": "user_joined",
                "room": room,
                "total_connections": len(self.rooms.get(room, set())),
                "timestamp": datetime.now().isoformat()
            }, exclude=[websocket])
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """
        Отключить WebSocket
        
        Args:
            websocket: WebSocket соединение для отключения
        """
        try:
            # Получаем метаданные перед удалением
            metadata = self.connection_metadata.get(websocket, {})
            room = metadata.get("room", "default")
            
            # Удаляем из активных соединений
            self.active_connections.discard(websocket)
            
            # Удаляем из комнаты
            if room in self.rooms:
                self.rooms[room].discard(websocket)
                # Удаляем пустые комнаты
                if not self.rooms[room]:
                    del self.rooms[room]
            
            # Удаляем метаданные
            self.connection_metadata.pop(websocket, None)
            
            logger.info(f"WebSocket disconnected from room '{room}'. Total connections: {len(self.active_connections)}")
            
            # Уведомляем остальных в комнате об отключении
            if room in self.rooms:
                await self.broadcast_to_room(room, {
                    "type": "user_left",
                    "room": room,
                    "total_connections": len(self.rooms[room]),
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Отправить сообщение конкретному WebSocket
        
        Args:
            websocket: Целевое WebSocket соединение
            message: Словарь с данными для отправки
        """
        try:
            if websocket in self.active_connections:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[List[WebSocket]] = None):
        """
        Отправить сообщение всем подключенным WebSocket
        
        Args:
            message: Словарь с данными для отправки
            exclude: Список WebSocket для исключения из рассылки
        """
        exclude = exclude or []
        disconnected = []
        
        for connection in self.active_connections:
            if connection not in exclude:
                try:
                    await connection.send_text(json.dumps(message, ensure_ascii=False))
                except WebSocketDisconnect:
                    disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any], exclude: Optional[List[WebSocket]] = None):
        """
        Отправить сообщение всем WebSocket в определенной комнате
        
        Args:
            room: Название комнаты
            message: Словарь с данными для отправки
            exclude: Список WebSocket для исключения из рассылки
        """
        exclude = exclude or []
        
        if room not in self.rooms:
            return
        
        disconnected = []
        
        for connection in self.rooms[room]:
            if connection not in exclude:
                try:
                    await connection.send_text(json.dumps(message, ensure_ascii=False))
                except WebSocketDisconnect:
                    disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error broadcasting to room {room}: {e}")
                    disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            await self.disconnect(connection)
    
    def get_connection_count(self, room: Optional[str] = None) -> int:
        """
        Получить количество активных соединений
        
        Args:
            room: Комната для подсчета (если None, то все соединения)
            
        Returns:
            int: Количество соединений
        """
        if room is None:
            return len(self.active_connections)
        else:
            return len(self.rooms.get(room, set()))
    
    def get_rooms_info(self) -> Dict[str, int]:
        """
        Получить информацию о всех комнатах
        
        Returns:
            Dict[str, int]: Словарь с названиями комнат и количеством соединений
        """
        return {room: len(connections) for room, connections in self.rooms.items()}
    
    def get_connection_metadata(self, websocket: WebSocket) -> Optional[Dict[str, Any]]:
        """
        Получить метаданные соединения
        
        Args:
            websocket: WebSocket соединение
            
        Returns:
            Optional[Dict[str, Any]]: Метаданные или None
        """
        return self.connection_metadata.get(websocket)
    
    async def ping_all(self):
        """Отправить ping всем активным соединениям"""
        await self.broadcast({
            "type": "ping",
            "timestamp": datetime.now().isoformat(),
            "server": "KittyCore 3.0"
        })
    
    async def send_system_notification(self, message: str, level: str = "info"):
        """
        Отправить системное уведомление всем соединениям
        
        Args:
            message: Текст уведомления
            level: Уровень важности (info, warning, error, success)
        """
        await self.broadcast({
            "type": "system_notification",
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        })


# Глобальный экземпляр менеджера (singleton pattern)
websocket_manager = WebSocketManager()


async def get_websocket_manager() -> WebSocketManager:
    """Dependency injection для получения WebSocket менеджера"""
    return websocket_manager 