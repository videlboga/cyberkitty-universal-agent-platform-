"""
KittyCore 3.0 Web Interface Module

Уберфутуристичный веб-интерфейс для управления агентными системами
с поддержкой динамических графов, real-time мониторинга и интерактивного управления.
"""

from .server import WebServer, create_app
from .websocket_manager import WebSocketManager

__version__ = "3.0.0"
__all__ = ["WebServer", "create_app", "WebSocketManager"] 