#!/usr/bin/env python3
"""
Упрощенный KittyCore 3.0 Web Interface
Без зависимостей от OrchestratorAgent
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Простой WebSocket менеджер
class SimpleWebSocketManager:
    def __init__(self):
        self.active_connections: set = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "message": "Подключение к KittyCore 3.0 установлено!"
        })
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except:
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            await self.disconnect(connection)

# Модели данных
class TaskRequest(BaseModel):
    prompt: str
    options: Optional[Dict] = {}

# Создаем приложение
app = FastAPI(
    title="KittyCore 3.0 Simple Web Interface",
    description="Упрощенный веб-интерфейс для агентных систем",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket менеджер
ws_manager = SimpleWebSocketManager()

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
                font-family: 'Consolas', 'Monaco', monospace;
                margin: 0; padding: 20px; background: #0a0a0a; color: #00ff41;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { 
                text-align: center; margin-bottom: 40px;
                border: 2px solid #00ff41; padding: 20px; border-radius: 10px;
            }
            .title {
                font-size: 3rem; margin: 0; text-shadow: 0 0 20px #00ff41;
            }
            .status { 
                background: #111; padding: 20px; border-radius: 8px; 
                margin-bottom: 20px;
            }
            .task-input { 
                width: 100%; min-height: 120px; background: #111; 
                color: #00ff41; border: 2px solid #333; padding: 15px;
                border-radius: 8px; font-family: monospace;
            }
            .button {
                background: #00ff41; color: #000; border: none; 
                padding: 15px 30px; border-radius: 8px; cursor: pointer;
                font-weight: bold; margin: 10px 5px;
            }
            .button:hover { background: #00cc33; }
            .log { 
                background: #111; padding: 20px; border-radius: 8px;
                max-height: 400px; overflow-y: auto; font-family: monospace;
                font-size: 12px; line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">🐱 KittyCore 3.0</h1>
                <p>Саморедуплицирующаяся Агентная Система (Simple Mode)</p>
            </div>
            
            <div class="status">
                <h3>🔗 Статус: <span id="status">Подключение...</span></h3>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3>💬 Отправить команду агентам</h3>
                <textarea id="task-input" class="task-input" 
                          placeholder="Введите задачу для выполнения агентами..."></textarea>
                <br><br>
                <button class="button" onclick="executeTask()">🚀 Выполнить</button>
                <button class="button" onclick="clearLog()">🗑️ Очистить</button>
            </div>
            
            <div>
                <h3>📋 Лог событий</h3>
                <div class="log" id="log"></div>
            </div>
        </div>
        
        <script>
            let ws = null;
            const log = document.getElementById('log');
            const status = document.getElementById('status');
            
            function connectWebSocket() {
                const wsUrl = 'ws://localhost:8003/ws';
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {
                    addLog('🟢 Подключено к KittyCore 3.0');
                    status.innerHTML = 'Подключено';
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addLog('📨 ' + JSON.stringify(data));
                };
                
                ws.onclose = function() {
                    addLog('🔴 Соединение закрыто');
                    status.innerHTML = 'Отключено';
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function addLog(message) {
                const timestamp = new Date().toLocaleTimeString();
                log.innerHTML += '[' + timestamp + '] ' + message + '<br>';
                log.scrollTop = log.scrollHeight;
            }
            
            function executeTask() {
                const input = document.getElementById('task-input');
                const task = input.value.trim();
                
                if (!task) return;
                
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'execute_task',
                        prompt: task,
                        task_id: 'task_' + Date.now()
                    }));
                    addLog('📤 Отправлена: ' + task);
                    input.value = '';
                }
            }
            
            function clearLog() {
                log.innerHTML = '';
            }
            
            connectWebSocket();
        </script>
    </body>
    </html>
    '''

@app.get("/api/status")
async def get_status():
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0-simple"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "execute_task":
                prompt = message.get('prompt', '')
                task_id = message.get('task_id', f'task_{int(datetime.now().timestamp() * 1000000)}')
                
                # Отправляем подтверждение получения
                await ws_manager.send_personal_message(websocket, {
                    "type": "task_received",
                    "task_id": task_id,
                    "prompt": prompt,
                    "timestamp": datetime.now().isoformat()
                })
                
                # ЗАПУСКАЕМ РЕАЛЬНУЮ СИСТЕМУ АГЕНТОВ
                try:
                    from kittycore.core.orchestrator import OrchestratorAgent
                    
                    orchestrator = OrchestratorAgent()
                    
                    # Отправляем статус начала обработки
                    await ws_manager.send_personal_message(websocket, {
                        "type": "task_processing",
                        "task_id": task_id,
                        "message": "🤖 Запускаем агентов...",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Выполняем задачу
                    result = await orchestrator.execute_task(prompt)
                    
                    # Обрабатываем результат (может быть строкой или словарем)
                    if isinstance(result, str):
                        # Если результат - строка, считаем задачу выполненной
                        success = True
                        result_data = {"message": result, "output": result}
                    elif isinstance(result, dict):
                        # Если результат - словарь, используем его напрямую
                        success = result.get('success', True)
                        result_data = result
                    else:
                        # Для других типов конвертируем в строку
                        success = True
                        result_data = {"message": str(result), "output": str(result)}
                    
                    # Отправляем результат
                    await ws_manager.send_personal_message(websocket, {
                        "type": "task_completed",
                        "task_id": task_id,
                        "result": result_data,
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    # Отправляем ошибку
                    await ws_manager.send_personal_message(websocket, {
                        "type": "task_error",
                        "task_id": task_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)

def main():
    print("🚀 KittyCore 3.0 Simple Web на http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")

if __name__ == "__main__":
    main() 