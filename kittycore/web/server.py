"""
KittyCore 3.0 Web Server

FastAPI-based веб-сервер с WebSocket поддержкой для real-time 
взаимодействия с агентными системами.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from .websocket_manager import WebSocketManager, websocket_manager

logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    """Модель запроса на выполнение задачи"""
    prompt: str
    options: Optional[Dict] = {}


class SystemStatus(BaseModel):
    """Модель статуса системы"""
    status: str
    timestamp: str
    active_connections: int
    rooms: Dict[str, int]
    version: str = "3.0.0"


def create_app() -> FastAPI:
    """Создать экземпляр FastAPI приложения"""
    
    app = FastAPI(
        title="KittyCore 3.0 Web Interface",
        description="Уберфутуристичный веб-интерфейс для агентных систем",
        version="3.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # CORS middleware для dev окружения
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В production указать конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Статические файлы (будем создавать фронтенд позже)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def index():
        """Главная страница"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>KittyCore 3.0</title>
            <meta charset="utf-8">
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; padding: 20px; background: #0a0a0a; color: #00ff41;
                }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .status { background: #111; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .input-area { margin-bottom: 20px; }
                textarea { 
                    width: 100%; min-height: 100px; background: #111; 
                    color: #00ff41; border: 1px solid #333; padding: 10px;
                    border-radius: 4px; font-family: monospace;
                }
                button {
                    background: #00ff41; color: #000; border: none; 
                    padding: 10px 20px; border-radius: 4px; cursor: pointer;
                    font-weight: bold;
                }
                button:hover { background: #00cc33; }
                .log { 
                    background: #111; padding: 20px; border-radius: 8px;
                    max-height: 400px; overflow-y: auto; font-family: monospace;
                    font-size: 12px; line-height: 1.4;
                }
                .log-entry { margin-bottom: 5px; }
                .log-timestamp { color: #666; }
                .log-info { color: #00ff41; }
                .log-warning { color: #ffaa00; }
                .log-error { color: #ff4444; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐱 KittyCore 3.0</h1>
                    <p>Саморедуплицирующаяся Агентная Система</p>
                </div>
                
                <div class="status" id="status">
                    <h3>Статус системы</h3>
                    <div id="connection-status">Подключение...</div>
                </div>
                
                <div class="input-area">
                    <h3>Команда для агентов</h3>
                    <textarea id="task-input" placeholder="Введите задачу для выполнения агентами..."></textarea>
                    <br><br>
                    <button onclick="executeTask()">🚀 Выполнить</button>
                </div>
                
                <div class="log" id="log">
                    <div class="log-entry">
                        <span class="log-timestamp">[SYSTEM]</span>
                        <span class="log-info">Ожидание подключения к KittyCore...</span>
                    </div>
                </div>
            </div>
            
            <script>
                let ws = null;
                const log = document.getElementById('log');
                const status = document.getElementById('connection-status');
                
                function connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = protocol + '//' + window.location.host + '/ws';
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function() {
                        addLog('Подключено к KittyCore 3.0', 'info');
                        status.innerHTML = '🟢 Подключено';
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        handleMessage(data);
                    };
                    
                    ws.onclose = function() {
                        addLog('Соединение закрыто', 'warning');
                        status.innerHTML = '🔴 Отключено';
                        setTimeout(connectWebSocket, 3000);
                    };
                    
                    ws.onerror = function(error) {
                        addLog('Ошибка WebSocket: ' + error, 'error');
                    };
                }
                
                function handleMessage(data) {
                    switch(data.type) {
                        case 'connection_established':
                            addLog('Соединение установлено (ID: ' + data.connection_id + ')', 'info');
                            break;
                        case 'system_notification':
                            addLog(data.message, data.level);
                            break;
                        case 'task_started':
                            addLog('Задача запущена: ' + data.task_id, 'info');
                            break;
                        case 'agent_spawned':
                            addLog('Создан агент: ' + data.agent_type, 'info');
                            break;
                        case 'task_completed':
                            addLog('Задача завершена: ' + data.result, 'info');
                            break;
                        default:
                            addLog('Получено: ' + JSON.stringify(data), 'info');
                    }
                }
                
                function addLog(message, level = 'info') {
                    const timestamp = new Date().toLocaleTimeString();
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    entry.innerHTML = 
                        '<span class="log-timestamp">[' + timestamp + ']</span> ' +
                        '<span class="log-' + level + '">' + message + '</span>';
                    log.appendChild(entry);
                    log.scrollTop = log.scrollHeight;
                }
                
                function executeTask() {
                    const input = document.getElementById('task-input');
                    const task = input.value.trim();
                    
                    if (!task) {
                        addLog('Введите задачу для выполнения', 'warning');
                        return;
                    }
                    
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            type: 'execute_task',
                            prompt: task,
                            timestamp: new Date().toISOString()
                        }));
                        addLog('Отправлена задача: ' + task, 'info');
                        input.value = '';
                    } else {
                        addLog('WebSocket не подключен', 'error');
                    }
                }
                
                // Запускаем подключение
                connectWebSocket();
                
                // Enter для отправки
                document.getElementById('task-input').addEventListener('keydown', function(event) {
                    if (event.ctrlKey && event.key === 'Enter') {
                        executeTask();
                    }
                });
            </script>
        </body>
        </html>
        '''
    
    @app.get("/api/status")
    async def get_status() -> SystemStatus:
        """Получить статус системы"""
        return SystemStatus(
            status="active",
            timestamp=datetime.now().isoformat(),
            active_connections=websocket_manager.get_connection_count(),
            rooms=websocket_manager.get_rooms_info()
        )
    
    @app.post("/api/task")
    async def execute_task(task: TaskRequest):
        """Выполнить задачу через REST API"""
        try:
            # Пока что просто отправляем уведомление через WebSocket
            await websocket_manager.send_system_notification(
                f"Получена задача через API: {task.prompt}",
                "info"
            )
            
            # TODO: Интеграция с OrchestratorAgent
            return {"status": "received", "task_id": f"task_{datetime.now().timestamp()}"}
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket эндпоинт для real-time коммуникации"""
        connected = await websocket_manager.connect(websocket, "main")
        
        if not connected:
            return
        
        try:
            while True:
                # Ожидаем сообщения от клиента
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Обрабатываем разные типы сообщений
                await handle_websocket_message(websocket, message)
                
        except WebSocketDisconnect:
            await websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket_manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, message: Dict):
    """Обработать сообщение от WebSocket клиента"""
    message_type = message.get("type")
    
    if message_type == "execute_task":
        prompt = message.get("prompt", "")
        
        # Уведомляем всех о начале выполнения задачи
        await websocket_manager.broadcast({
            "type": "task_started",
            "prompt": prompt,
            "task_id": f"task_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        })
        
        # TODO: Интеграция с OrchestratorAgent
        # Пока что симулируем выполнение
        await asyncio.sleep(1)
        
        await websocket_manager.send_personal_message(websocket, {
            "type": "task_completed",
            "result": f"Задача '{prompt}' принята к выполнению (демо режим)",
            "timestamp": datetime.now().isoformat()
        })
        
    elif message_type == "ping":
        await websocket_manager.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })


class WebServer:
    """Основной класс веб-сервера KittyCore"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = create_app()
    
    def run(self, **kwargs):
        """Запустить сервер"""
        logger.info(f"Запуск KittyCore 3.0 Web Server на {self.host}:{self.port}")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            **kwargs
        )
    
    async def start_async(self):
        """Запустить сервер асинхронно"""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    server = WebServer()
    server.run() 