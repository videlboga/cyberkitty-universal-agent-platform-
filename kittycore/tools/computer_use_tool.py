"""
ComputerUseTool для KittyCore 3.0
Оптимизирован для Manjaro i3 X11 с OpenRouter API

ЧАСТЬ 1: Базовая структура и зависимости
"""

import asyncio
import base64
import json
import os
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import platform

# Основные библиотеки для GUI автоматизации
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Linux X11 специфичные
try:
    from Xlib import X, display
    from Xlib.ext.xtest import fake_input
    X11_AVAILABLE = True
except ImportError:
    X11_AVAILABLE = False

from .base_tool import BaseTool


class EnvironmentDetector:
    """Детектор среды выполнения"""
    
    @staticmethod
    def detect():
        """Определение среды выполнения"""
        return EnvironmentInfo(
            platform=platform.system(),
            is_linux=platform.system() == "Linux",
            is_windows=platform.system() == "Windows", 
            is_macos=platform.system() == "Darwin",
            has_x11=EnvironmentDetector._detect_x11(),
            has_wayland=EnvironmentDetector._detect_wayland(),
            wm_name=EnvironmentDetector._detect_window_manager()
        )
    
    @staticmethod 
    def _detect_x11() -> bool:
        """Проверка наличия X11"""
        return os.environ.get('DISPLAY') is not None
    
    @staticmethod
    def _detect_wayland() -> bool:
        """Проверка наличия Wayland"""
        return os.environ.get('WAYLAND_DISPLAY') is not None
    
    @staticmethod
    def _detect_window_manager() -> str:
        """Определение оконного менеджера"""
        # Проверяем переменные среды
        if os.environ.get('I3SOCK'):
            return "i3"
        elif os.environ.get('SWAY_SOCK'):
            return "sway"
        elif os.environ.get('DESKTOP_SESSION'):
            return os.environ.get('DESKTOP_SESSION', 'unknown')
        else:
            return "unknown"


@dataclass
class EnvironmentInfo:
    """Информация о среде выполнения"""
    platform: str
    is_linux: bool = False
    is_windows: bool = False
    is_macos: bool = False
    has_x11: bool = False
    has_wayland: bool = False
    wm_name: str = "unknown"


@dataclass
class ScreenInfo:
    """Информация о экране"""
    width: int
    height: int
    scale_factor: float = 1.0
    display_name: str = ":0"


@dataclass
class ActionResult:
    """Результат выполнения действия"""
    success: bool
    action_type: str
    details: Dict[str, Any]
    screenshot_path: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0


class ComputerUseTool(BaseTool):
    """
    ComputerUseTool для автоматизации GUI в Manjaro i3 X11
    Поддерживает скриншоты, клики, ввод текста и навигацию
    """
    
    def __init__(self):
        super().__init__()
        self.name = "computer_use"
        self.description = "Инструмент для автоматизации GUI - скриншоты, клики, ввод текста"
        
        # Инициализация среды
        self.env_info = EnvironmentDetector.detect()
        self.backend = self._select_best_backend()
        
        # Настройка PyAutoGUI для i3wm
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = False  # Отключаем failsafe углы для i3
            pyautogui.PAUSE = 0.1  # Небольшая пауза между действиями
        
        # Кэш для скриншотов
        self._screenshot_cache = {}
        self._last_screenshot_time = 0
    
    def _select_best_backend(self) -> str:
        """Выбираем лучший доступный backend"""
        if self.env_info.is_linux and PYAUTOGUI_AVAILABLE:
            return "pyautogui"
        elif PYNPUT_AVAILABLE:
            return "pynput"
        elif self.env_info.is_linux:
            return "x11_native"
        else:
            return "fallback"
    
    @property
    def json_schema(self) -> Dict[str, Any]:
        """JSON Schema для ComputerUseTool с базовыми действиями"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        # Базовые действия
                        "screenshot",
                        "click", 
                        "type_text",
                        "key_press",
                        
                        # Расширенные действия (ЧАСТЬ 3)
                        "double_click",
                        "right_click", 
                        "drag_and_drop",
                        "scroll",
                        "mouse_move",
                        "hold_key",
                        "key_combination",
                        
                        # Работа с окнами
                        "focus_window",
                        "resize_window", 
                        "move_window",
                        "minimize_window",
                        "maximize_window",
                        "close_window",
                        
                        # Поиск элементов (простой)
                        "find_text_on_screen",
                        "find_image_on_screen",
                        "wait_for_element",
                        
                        # Информационные
                        "get_screen_info",
                        "get_mouse_position",
                        "get_active_window",
                        "list_windows",
                        
                        # Диагностика
                        "test_environment",
                        "check_capabilities"
                    ],
                    "description": "Действие для выполнения"
                },
                "x": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "X координата для клика или позиционирования"
                },
                "y": {
                    "type": "integer", 
                    "minimum": 0,
                    "description": "Y координата для клика или позиционирования"
                },
                "text": {
                    "type": "string",
                    "description": "Текст для ввода"
                },
                "key": {
                    "type": "string",
                    "enum": ["enter", "tab", "escape", "space", "backspace", "delete", "home", "end", "up", "down", "left", "right", "ctrl", "alt", "shift"],
                    "description": "Клавиша для нажатия"
                },
                "button": {
                    "type": "string",
                    "enum": ["left", "right", "middle"],
                    "default": "left",
                    "description": "Кнопка мыши для клика"
                },
                "save_path": {
                    "type": "string",
                    "description": "Путь для сохранения скриншота"
                },
                "region": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}, 
                        "width": {"type": "integer"},
                        "height": {"type": "integer"}
                    },
                    "description": "Регион экрана для скриншота"
                },
                "to_x": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Конечная X координата для drag&drop"
                },
                "to_y": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Конечная Y координата для drag&drop"
                },
                "scroll_direction": {
                    "type": "string",
                    "enum": ["up", "down", "left", "right"],
                    "description": "Направление прокрутки"
                },
                "scroll_amount": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 3,
                    "description": "Количество прокруток (1-10)"
                },
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список клавиш для комбинации (например: ['ctrl', 'c'])"
                },
                "window_name": {
                    "type": "string",
                    "description": "Название окна для фокуса/управления"
                },
                "window_id": {
                    "type": "string",
                    "description": "ID окна для управления"
                },
                "search_text": {
                    "type": "string",
                    "description": "Текст для поиска на экране"
                },
                "image_path": {
                    "type": "string",
                    "description": "Путь к изображению для поиска"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 60,
                    "default": 10,
                    "description": "Таймаут ожидания в секундах"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 1.0,
                    "default": 0.8,
                    "description": "Уровень точности поиска изображения (0.1-1.0)"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение действий ComputerUseTool"""
        action = params.get("action")
        
        try:
            # Базовые действия
            if action == "screenshot":
                return await self._take_screenshot(params)
            elif action == "click":
                return await self._click(params)
            elif action == "type_text":
                return await self._type_text(params)
            elif action == "key_press":
                return await self._key_press(params)
                
            # Расширенные действия (ЧАСТЬ 3)
            elif action == "double_click":
                return await self._double_click(params)
            elif action == "right_click":
                return await self._right_click(params)
            elif action == "drag_and_drop":
                return await self._drag_and_drop(params)
            elif action == "scroll":
                return await self._scroll(params)
            elif action == "mouse_move":
                return await self._mouse_move(params)
            elif action == "hold_key":
                return await self._hold_key(params)
            elif action == "key_combination":
                return await self._key_combination(params)
                
            # Работа с окнами
            elif action == "focus_window":
                return await self._focus_window(params)
            elif action == "resize_window":
                return await self._resize_window(params)
            elif action == "move_window":
                return await self._move_window(params)
            elif action == "minimize_window":
                return await self._minimize_window(params)
            elif action == "maximize_window":
                return await self._maximize_window(params)
            elif action == "close_window":
                return await self._close_window(params)
                
            # Поиск элементов
            elif action == "find_text_on_screen":
                return await self._find_text_on_screen(params)
            elif action == "find_image_on_screen":
                return await self._find_image_on_screen(params)
            elif action == "wait_for_element":
                return await self._wait_for_element(params)
                
            # Информационные действия
            elif action == "get_screen_info":
                return await self._get_screen_info()
            elif action == "get_mouse_position":
                return await self._get_mouse_position()
            elif action == "get_active_window":
                return await self._get_active_window()
            elif action == "list_windows":
                return await self._list_windows()
                
            # Диагностика
            elif action == "test_environment":
                return await self._test_environment()
            elif action == "check_capabilities":
                return await self._check_capabilities()
            else:
                return {
                    "success": False,
                    "error": f"Неизвестное действие: {action}",
                    "available_actions": list(self.json_schema["properties"]["action"]["enum"])
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка выполнения {action}: {str(e)}",
                "backend": self.backend,
                "environment": asdict(self.env_info)
            }
    
    async def _key_press(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Нажатие клавиши"""
        key = params.get("key")
        
        if not key:
            return {
                "success": False,
                "error": "Требуется параметр key для нажатия клавиши"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                pyautogui.press(key)
                return {
                    "success": True,
                    "action": "key_press",
                    "key": key,
                    "backend": "pyautogui"
                }
                
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                
                # Маппинг специальных клавиш
                key_map = {
                    "enter": Key.enter,
                    "tab": Key.tab,
                    "escape": Key.esc,
                    "space": Key.space,
                    "backspace": Key.backspace,
                    "delete": Key.delete,
                    "home": Key.home,
                    "end": Key.end,
                    "up": Key.up,
                    "down": Key.down,
                    "left": Key.left,
                    "right": Key.right,
                    "ctrl": Key.ctrl,
                    "alt": Key.alt,
                    "shift": Key.shift
                }
                
                pynput_key = key_map.get(key, key)
                keyboard_controller.press(pynput_key)
                keyboard_controller.release(pynput_key)
                
                return {
                    "success": True,
                    "action": "key_press",
                    "key": key,
                    "backend": "pynput"
                }
                
            elif self.backend == "x11_native":
                # X11 нативные клавиши через xdotool
                key_map = {
                    "enter": "Return",
                    "tab": "Tab",
                    "escape": "Escape",
                    "space": "space",
                    "backspace": "BackSpace",
                    "delete": "Delete",
                    "home": "Home",
                    "end": "End",
                    "up": "Up",
                    "down": "Down", 
                    "left": "Left",
                    "right": "Right",
                    "ctrl": "ctrl",
                    "alt": "alt",
                    "shift": "shift"
                }
                
                xdotool_key = key_map.get(key, key)
                cmd = f"xdotool key {xdotool_key}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "key_press",
                    "key": key,
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для нажатия клавиш",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка нажатия клавиши: {str(e)}",
                "key": key,
                "backend": self.backend
            }
    
    async def _get_mouse_position(self) -> Dict[str, Any]:
        """Получение текущей позиции мыши"""
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                x, y = pyautogui.position()
                return {
                    "success": True,
                    "position": {"x": x, "y": y},
                    "backend": "pyautogui"
                }
                
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                x, y = mouse_controller.position
                return {
                    "success": True,
                    "position": {"x": x, "y": y},
                    "backend": "pynput"
                }
                
            elif self.backend == "x11_native":
                # X11 позиция мыши через xdotool
                cmd = "xdotool getmouselocation --shell"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Парсинг вывода X=123\nY=456\nSCREEN=0\nWINDOW=789
                    lines = result.stdout.strip().split('\n')
                    x = int(lines[0].split('=')[1])
                    y = int(lines[1].split('=')[1])
                    
                    return {
                        "success": True,
                        "position": {"x": x, "y": y},
                        "backend": "x11_xdotool"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"xdotool ошибка: {result.stderr}",
                        "backend": "x11_xdotool"
                    }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для получения позиции мыши",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка получения позиции мыши: {str(e)}",
                "backend": self.backend
            }
    
    async def _get_active_window(self) -> Dict[str, Any]:
        """Получение информации об активном окне"""
        try:
            if self.env_info.is_linux:
                # Linux - используем xdotool для получения активного окна
                cmd = "xdotool getactivewindow getwindowname"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    window_name = result.stdout.strip()
                    
                    # Получаем размеры окна
                    cmd_size = "xdotool getactivewindow getwindowgeometry --shell"
                    result_size = subprocess.run(cmd_size, shell=True, capture_output=True, text=True)
                    
                    geometry = {}
                    if result_size.returncode == 0:
                        lines = result_size.stdout.strip().split('\n')
                        for line in lines:
                            if '=' in line:
                                key, value = line.split('=', 1)
                                geometry[key.lower()] = value
                    
                    return {
                        "success": True,
                        "window_name": window_name,
                        "geometry": geometry,
                        "backend": "x11_xdotool"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"xdotool ошибка: {result.stderr}",
                        "backend": "x11_xdotool"
                    }
            else:
                return {
                    "success": False,
                    "error": "Получение активного окна поддерживается только на Linux",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка получения активного окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _test_environment(self) -> Dict[str, Any]:
        """Тестирование среды выполнения"""
        try:
            results = {
                "success": True,
                "environment": asdict(self.env_info),
                "backend": self.backend,
                "available_backends": {
                    "pyautogui": PYAUTOGUI_AVAILABLE,
                    "pynput": PYNPUT_AVAILABLE,
                    "opencv": OPENCV_AVAILABLE,
                    "x11": X11_AVAILABLE
                },
                "tests": {}
            }
            
            # Тест скриншота
            screenshot_result = await self._take_screenshot({"save_path": "/tmp/kittycore_test.png"})
            results["tests"]["screenshot"] = screenshot_result["success"]
            
            # Тест позиции мыши
            mouse_result = await self._get_mouse_position()
            results["tests"]["mouse_position"] = mouse_result["success"]
            
            # Тест активного окна (только Linux)
            if self.env_info.is_linux:
                window_result = await self._get_active_window()
                results["tests"]["active_window"] = window_result["success"]
            
            # Общий успех
            results["success"] = all(results["tests"].values())
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка тестирования среды: {str(e)}",
                "backend": self.backend
            }
    
    async def _check_capabilities(self) -> Dict[str, Any]:
        """Проверка возможностей инструмента"""
        capabilities = {
            "screenshot": False,
            "click": False,
            "type_text": False,
            "key_press": False,
            "mouse_position": False,
            "active_window": False
        }
        
        # Проверяем каждую возможность
        if PYAUTOGUI_AVAILABLE or X11_AVAILABLE:
            capabilities["screenshot"] = True
            capabilities["click"] = True
            capabilities["type_text"] = True
            capabilities["key_press"] = True
            capabilities["mouse_position"] = True
            
        if self.env_info.is_linux:
            capabilities["active_window"] = True
            
        if PYNPUT_AVAILABLE:
            capabilities["click"] = True
            capabilities["type_text"] = True
            capabilities["key_press"] = True
            capabilities["mouse_position"] = True
        
        return {
            "success": True,
            "capabilities": capabilities,
            "backend": self.backend,
            "environment": asdict(self.env_info),
            "available_libraries": {
                "pyautogui": PYAUTOGUI_AVAILABLE,
                "pynput": PYNPUT_AVAILABLE,
                "opencv": OPENCV_AVAILABLE,
                "x11": X11_AVAILABLE
            }
        }
    
    # === ЧАСТЬ 3: РАСШИРЕННЫЕ ДЕЙСТВИЯ ===
    
    async def _double_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Двойной клик мышью"""
        x = params.get("x")
        y = params.get("y")
        
        if x is None or y is None:
            return {
                "success": False,
                "error": "Требуются координаты x и y для двойного клика"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                pyautogui.doubleClick(x, y)
                return {
                    "success": True,
                    "action": "double_click",
                    "coordinates": [x, y],
                    "backend": "pyautogui"
                }
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                mouse_controller.position = (x, y)
                mouse_controller.click(Button.left, 2)  # Double click
                return {
                    "success": True,
                    "action": "double_click",
                    "coordinates": [x, y],
                    "backend": "pynput"
                }
            elif self.backend == "x11_native":
                cmd = f"xdotool mousemove {x} {y} click --repeat 2 1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "action": "double_click",
                    "coordinates": [x, y],
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для двойного клика",
                    "backend": self.backend
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка двойного клика: {str(e)}",
                "backend": self.backend
            }
    
    async def _right_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Правый клик мышью"""
        x = params.get("x")
        y = params.get("y")
        
        if x is None or y is None:
            return {
                "success": False,
                "error": "Требуются координаты x и y для правого клика"
            }
        
        # Используем существующий метод _click с параметром button="right"
        params["button"] = "right"
        return await self._click(params)
    
    async def _drag_and_drop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Перетаскивание (drag and drop)"""
        x = params.get("x")
        y = params.get("y")
        to_x = params.get("to_x")
        to_y = params.get("to_y")
        
        if any(coord is None for coord in [x, y, to_x, to_y]):
            return {
                "success": False,
                "error": "Требуются координаты x, y, to_x, to_y для drag&drop"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                pyautogui.drag(to_x - x, to_y - y, x, y, duration=0.5)
                return {
                    "success": True,
                    "action": "drag_and_drop",
                    "from": [x, y],
                    "to": [to_x, to_y],
                    "backend": "pyautogui"
                }
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                # Переходим к начальной позиции
                mouse_controller.position = (x, y)
                # Зажимаем левую кнопку
                mouse_controller.press(Button.left)
                time.sleep(0.1)
                # Перетаскиваем к конечной позиции
                mouse_controller.position = (to_x, to_y)
                time.sleep(0.1)
                # Отпускаем кнопку
                mouse_controller.release(Button.left)
                return {
                    "success": True,
                    "action": "drag_and_drop",
                    "from": [x, y],
                    "to": [to_x, to_y],
                    "backend": "pynput"
                }
            elif self.backend == "x11_native":
                cmd = f"xdotool mousemove {x} {y} mousedown 1 mousemove {to_x} {to_y} mouseup 1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "action": "drag_and_drop",
                    "from": [x, y],
                    "to": [to_x, to_y],
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для drag&drop",
                    "backend": self.backend
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка drag&drop: {str(e)}",
                "backend": self.backend
            }
    
    async def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Прокрутка колесом мыши"""
        direction = params.get("scroll_direction", "down")
        amount = params.get("scroll_amount", 3)
        x = params.get("x")
        y = params.get("y")
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                # Переходим к позиции если указана
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y)
                
                # Определяем направление прокрутки
                if direction == "up":
                    pyautogui.scroll(amount)
                elif direction == "down":
                    pyautogui.scroll(-amount)
                elif direction in ["left", "right"]:
                    # PyAutoGUI не поддерживает горизонтальную прокрутку напрямую
                    return {
                        "success": False,
                        "error": "PyAutoGUI не поддерживает горизонтальную прокрутку",
                        "backend": "pyautogui"
                    }
                
                return {
                    "success": True,
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "position": [x, y] if x and y else None,
                    "backend": "pyautogui"
                }
                
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                
                # Переходим к позиции если указана
                if x is not None and y is not None:
                    mouse_controller.position = (x, y)
                
                # Прокрутка
                for _ in range(amount):
                    if direction == "up":
                        mouse_controller.scroll(0, 1)
                    elif direction == "down":
                        mouse_controller.scroll(0, -1)
                    elif direction == "left":
                        mouse_controller.scroll(-1, 0)
                    elif direction == "right":
                        mouse_controller.scroll(1, 0)
                    time.sleep(0.1)
                
                return {
                    "success": True,
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "position": [x, y] if x and y else None,
                    "backend": "pynput"
                }
                
            elif self.backend == "x11_native":
                # X11 прокрутка через xdotool
                position_cmd = f"xdotool mousemove {x} {y}" if x and y else ""
                
                # Маппинг направлений на кнопки колеса мыши
                button_map = {
                    "up": "4",
                    "down": "5",
                    "left": "6", 
                    "right": "7"
                }
                
                button = button_map.get(direction, "5")
                scroll_cmd = f"xdotool click --repeat {amount} {button}"
                
                cmd = f"{position_cmd} {scroll_cmd}".strip()
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "position": [x, y] if x and y else None,
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для прокрутки",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка прокрутки: {str(e)}",
                "backend": self.backend
            }
    
    async def _mouse_move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Перемещение мыши без клика"""
        x = params.get("x")
        y = params.get("y")
        
        if x is None or y is None:
            return {
                "success": False,
                "error": "Требуются координаты x и y для перемещения мыши"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                pyautogui.moveTo(x, y)
                return {
                    "success": True,
                    "action": "mouse_move",
                    "coordinates": [x, y],
                    "backend": "pyautogui"
                }
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                mouse_controller.position = (x, y)
                return {
                    "success": True,
                    "action": "mouse_move",
                    "coordinates": [x, y],
                    "backend": "pynput"
                }
            elif self.backend == "x11_native":
                cmd = f"xdotool mousemove {x} {y}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "action": "mouse_move",
                    "coordinates": [x, y],
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для перемещения мыши",
                    "backend": self.backend
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка перемещения мыши: {str(e)}",
                "backend": self.backend
            }
    
    async def _hold_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Удержание клавиши (зажатие)"""
        key = params.get("key")
        
        if not key:
            return {
                "success": False,
                "error": "Требуется параметр key для удержания клавиши"
            }
        
        try:
            if self.backend == "pynput" and PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                
                # Маппинг клавиш
                key_map = {
                    "ctrl": Key.ctrl,
                    "alt": Key.alt,
                    "shift": Key.shift,
                    "enter": Key.enter,
                    "tab": Key.tab,
                    "escape": Key.esc,
                    "space": Key.space
                }
                
                pynput_key = key_map.get(key, key)
                keyboard_controller.press(pynput_key)
                
                return {
                    "success": True,
                    "action": "hold_key",
                    "key": key,
                    "backend": "pynput",
                    "note": "Клавиша удерживается. Используйте key_press для отпускания."
                }
            else:
                return {
                    "success": False,
                    "error": "hold_key поддерживается только с pynput backend",
                    "backend": self.backend
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка удержания клавиши: {str(e)}",
                "backend": self.backend
            }
    
    async def _key_combination(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Комбинация клавиш (например Ctrl+C)"""
        keys = params.get("keys", [])
        
        if not keys or len(keys) < 2:
            return {
                "success": False,
                "error": "Требуется массив из минимум 2 клавиш для комбинации"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                # PyAutoGUI поддерживает комбинации через hotkey
                pyautogui.hotkey(*keys)
                return {
                    "success": True,
                    "action": "key_combination",
                    "keys": keys,
                    "backend": "pyautogui"
                }
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                
                # Маппинг клавиш
                key_map = {
                    "ctrl": Key.ctrl,
                    "alt": Key.alt,
                    "shift": Key.shift,
                    "cmd": Key.cmd,
                    "enter": Key.enter,
                    "tab": Key.tab,
                    "escape": Key.esc,
                    "space": Key.space
                }
                
                # Преобразуем клавиши
                pynput_keys = []
                for key in keys:
                    pynput_keys.append(key_map.get(key, key))
                
                # Зажимаем все клавиши
                for key in pynput_keys:
                    keyboard_controller.press(key)
                
                # Небольшая задержка
                time.sleep(0.1)
                
                # Отпускаем в обратном порядке
                for key in reversed(pynput_keys):
                    keyboard_controller.release(key)
                
                return {
                    "success": True,
                    "action": "key_combination",
                    "keys": keys,
                    "backend": "pynput"
                }
            elif self.backend == "x11_native":
                # X11 комбинации через xdotool
                key_combo = "+".join(keys)
                cmd = f"xdotool key {key_combo}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "key_combination",
                    "keys": keys,
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для комбинаций клавиш",
                    "backend": self.backend
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка комбинации клавиш: {str(e)}",
                "backend": self.backend
            }
    
    async def _list_windows(self) -> Dict[str, Any]:
        """Список всех открытых окон (Linux i3wm)"""
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Список окон поддерживается только на Linux",
                    "backend": self.backend
                }
            
            # Получаем список окон через wmctrl
            cmd = "wmctrl -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Fallback на xdotool
                cmd_fallback = "xdotool search --name '.*'"
                result_fallback = subprocess.run(cmd_fallback, shell=True, capture_output=True, text=True)
                
                if result_fallback.returncode == 0:
                    window_ids = result_fallback.stdout.strip().split('\n')
                    windows = []
                    
                    for window_id in window_ids[:10]:  # Ограничиваем до 10 окон
                        if window_id:
                            # Получаем название окна
                            cmd_name = f"xdotool getwindowname {window_id}"
                            result_name = subprocess.run(cmd_name, shell=True, capture_output=True, text=True)
                            window_name = result_name.stdout.strip() if result_name.returncode == 0 else "Unknown"
                            
                            windows.append({
                                "id": window_id,
                                "name": window_name
                            })
                    
                    return {
                        "success": True,
                        "windows": windows,
                        "count": len(windows),
                        "backend": "x11_xdotool"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"wmctrl и xdotool недоступны: {result.stderr}",
                        "backend": "x11_fallback"
                    }
            
            # Парсим вывод wmctrl
            windows = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line:
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        windows.append({
                            "id": parts[0],
                            "desktop": parts[1], 
                            "pid": parts[2],
                            "name": parts[3]
                        })
            
            return {
                "success": True,
                "windows": windows,
                "count": len(windows),
                "backend": "wmctrl"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка получения списка окон: {str(e)}",
                "backend": self.backend
            }
    
    # === ЧАСТЬ 4: УПРАВЛЕНИЕ ОКНАМИ I3WM + ПОИСК ЭЛЕМЕНТОВ ===
    
    async def _focus_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Фокус на окно по названию или ID"""
        window_name = params.get("window_name")
        window_id = params.get("window_id")
        
        if not window_name and not window_id:
            return {
                "success": False,
                "error": "Требуется window_name или window_id"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Управление окнами поддерживается только на Linux",
                    "backend": self.backend
                }
            
            if window_id:
                # Фокус по ID
                if self.env_info.wm_name == "i3":
                    cmd = f"i3-msg '[id=\"{window_id}\"] focus'"
                else:
                    cmd = f"wmctrl -i -a {window_id}"
            else:
                # Фокус по названию
                if self.env_info.wm_name == "i3":
                    cmd = f"i3-msg '[title=\"{window_name}\"] focus'"
                else:
                    cmd = f"wmctrl -a '{window_name}'"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "action": "focus_window",
                "window_name": window_name,
                "window_id": window_id,
                "wm": self.env_info.wm_name,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка фокуса окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _resize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Изменение размера окна"""
        window_id = params.get("window_id")
        width = params.get("width")
        height = params.get("height")
        
        if not window_id or not width or not height:
            return {
                "success": False,
                "error": "Требуются window_id, width и height"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Изменение размера окон поддерживается только на Linux"
                }
            
            if self.env_info.wm_name == "i3":
                # i3wm не поддерживает прямое изменение размера окон (тайлинговый WM)
                return {
                    "success": False,
                    "error": "i3wm не поддерживает изменение размера окон (тайлинговый WM)",
                    "suggestion": "Используйте i3-resize команды вместо этого"
                }
            else:
                # Обычные WM через wmctrl
                cmd = f"wmctrl -i -r {window_id} -e 0,-1,-1,{width},{height}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "resize_window",
                    "window_id": window_id,
                    "new_size": [width, height],
                    "error": result.stderr if result.returncode != 0 else None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка изменения размера окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _move_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Перемещение окна"""
        window_id = params.get("window_id")
        x = params.get("x")
        y = params.get("y")
        
        if not window_id or x is None or y is None:
            return {
                "success": False,
                "error": "Требуются window_id, x и y"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Перемещение окон поддерживается только на Linux"
                }
            
            if self.env_info.wm_name == "i3":
                # i3wm не поддерживает свободное перемещение окон
                return {
                    "success": False,
                    "error": "i3wm не поддерживает свободное перемещение окон (тайлинговый WM)",
                    "suggestion": "Используйте move container to workspace/output команды"
                }
            else:
                # Обычные WM через wmctrl
                cmd = f"wmctrl -i -r {window_id} -e 0,{x},{y},-1,-1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "move_window",
                    "window_id": window_id,
                    "new_position": [x, y],
                    "error": result.stderr if result.returncode != 0 else None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка перемещения окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _minimize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Минимизация окна"""
        window_id = params.get("window_id")
        window_name = params.get("window_name")
        
        if not window_id and not window_name:
            return {
                "success": False,
                "error": "Требуется window_id или window_name"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Минимизация окон поддерживается только на Linux"
                }
            
            if self.env_info.wm_name == "i3":
                # В i3wm нет минимизации, но можно переместить в scratchpad
                if window_id:
                    cmd = f"i3-msg '[id=\"{window_id}\"] move scratchpad'"
                else:
                    cmd = f"i3-msg '[title=\"{window_name}\"] move scratchpad'"
            else:
                # Обычные WM через xdotool
                if window_id:
                    cmd = f"xdotool windowminimize {window_id}"
                else:
                    cmd = f"xdotool search --name '{window_name}' windowminimize"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "action": "minimize_window",
                "window_id": window_id,
                "window_name": window_name,
                "wm": self.env_info.wm_name,
                "note": "В i3wm окно перемещено в scratchpad" if self.env_info.wm_name == "i3" else None,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка минимизации окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _maximize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Максимизация окна"""
        window_id = params.get("window_id")
        window_name = params.get("window_name")
        
        if not window_id and not window_name:
            return {
                "success": False,
                "error": "Требуется window_id или window_name"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Максимизация окон поддерживается только на Linux"
                }
            
            if self.env_info.wm_name == "i3":
                # В i3wm используем fullscreen режим
                if window_id:
                    cmd = f"i3-msg '[id=\"{window_id}\"] fullscreen toggle'"
                else:
                    cmd = f"i3-msg '[title=\"{window_name}\"] fullscreen toggle'"
            else:
                # Обычные WM через wmctrl
                if window_id:
                    cmd = f"wmctrl -i -r {window_id} -b toggle,maximized_vert,maximized_horz"
                else:
                    cmd = f"wmctrl -r '{window_name}' -b toggle,maximized_vert,maximized_horz"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "action": "maximize_window",
                "window_id": window_id,
                "window_name": window_name,
                "wm": self.env_info.wm_name,
                "note": "В i3wm используется fullscreen toggle" if self.env_info.wm_name == "i3" else None,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка максимизации окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _close_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Закрытие окна"""
        window_id = params.get("window_id")
        window_name = params.get("window_name")
        
        if not window_id and not window_name:
            return {
                "success": False,
                "error": "Требуется window_id или window_name"
            }
        
        try:
            if not self.env_info.is_linux:
                return {
                    "success": False,
                    "error": "Закрытие окон поддерживается только на Linux"
                }
            
            if self.env_info.wm_name == "i3":
                # i3wm команды
                if window_id:
                    cmd = f"i3-msg '[id=\"{window_id}\"] kill'"
                else:
                    cmd = f"i3-msg '[title=\"{window_name}\"] kill'"
            else:
                # Обычные WM через wmctrl
                if window_id:
                    cmd = f"wmctrl -i -c {window_id}"
                else:
                    cmd = f"wmctrl -c '{window_name}'"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "action": "close_window",
                "window_id": window_id,
                "window_name": window_name,
                "wm": self.env_info.wm_name,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка закрытия окна: {str(e)}",
                "backend": self.backend
            }
    
    async def _find_text_on_screen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Поиск текста на экране (базовая реализация)"""
        search_text = params.get("search_text")
        
        if not search_text:
            return {
                "success": False,
                "error": "Требуется параметр search_text"
            }
        
        try:
            # Базовая реализация - создаём скриншот и ищем текст
            # В реальной реализации здесь был бы OCR (tesseract)
            
            # Создаём временный скриншот
            screenshot_result = await self._take_screenshot({"save_path": "/tmp/kittycore_text_search.png"})
            
            if not screenshot_result["success"]:
                return {
                    "success": False,
                    "error": f"Не удалось создать скриншот для поиска текста: {screenshot_result.get('error')}"
                }
            
            return {
                "success": False,
                "error": "Поиск текста требует установки tesseract-ocr",
                "suggestion": "sudo pacman -S tesseract tesseract-data-rus tesseract-data-eng",
                "screenshot_path": screenshot_result["screenshot_path"],
                "note": "Базовая реализация. Для полной функциональности нужен OCR."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка поиска текста: {str(e)}",
                "backend": self.backend
            }
    
    async def _find_image_on_screen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Поиск изображения на экране"""
        image_path = params.get("image_path")
        confidence = params.get("confidence", 0.8)
        
        if not image_path:
            return {
                "success": False,
                "error": "Требуется параметр image_path"
            }
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Файл изображения не найден: {image_path}"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                # PyAutoGUI поддерживает поиск изображений
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                
                if location:
                    center = pyautogui.center(location)
                    return {
                        "success": True,
                        "found": True,
                        "location": {
                            "x": location.left,
                            "y": location.top,
                            "width": location.width,
                            "height": location.height
                        },
                        "center": {"x": center.x, "y": center.y},
                        "confidence": confidence,
                        "backend": "pyautogui"
                    }
                else:
                    return {
                        "success": True,
                        "found": False,
                        "confidence": confidence,
                        "backend": "pyautogui"
                    }
            
            elif OPENCV_AVAILABLE:
                # OpenCV template matching fallback
                return {
                    "success": False,
                    "error": "OpenCV поиск изображений не реализован в этой версии",
                    "suggestion": "Используйте PyAutoGUI backend"
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для поиска изображений",
                    "available_backends": [self.backend],
                    "pyautogui_available": PYAUTOGUI_AVAILABLE,
                    "opencv_available": OPENCV_AVAILABLE
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка поиска изображения: {str(e)}",
                "backend": self.backend
            }
    
    async def _wait_for_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ожидание появления элемента (изображения или текста)"""
        image_path = params.get("image_path")
        search_text = params.get("search_text")
        timeout = params.get("timeout", 10)
        confidence = params.get("confidence", 0.8)
        
        if not image_path and not search_text:
            return {
                "success": False,
                "error": "Требуется image_path или search_text"
            }
        
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if image_path:
                    # Ждём изображение
                    result = await self._find_image_on_screen({
                        "image_path": image_path,
                        "confidence": confidence
                    })
                    
                    if result["success"] and result.get("found"):
                        return {
                            "success": True,
                            "found": True,
                            "element_type": "image",
                            "wait_time": time.time() - start_time,
                            "location": result.get("location"),
                            "center": result.get("center")
                        }
                
                elif search_text:
                    # Ждём текст
                    result = await self._find_text_on_screen({
                        "search_text": search_text
                    })
                    
                    if result["success"] and result.get("found"):
                        return {
                            "success": True,
                            "found": True,
                            "element_type": "text",
                            "wait_time": time.time() - start_time,
                            "text": search_text
                        }
                
                # Пауза между проверками
                await asyncio.sleep(0.5)
            
            # Таймаут
            return {
                "success": True,
                "found": False,
                "timeout": timeout,
                "element_type": "image" if image_path else "text",
                "waited_time": timeout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка ожидания элемента: {str(e)}",
                "backend": self.backend
            }
    
    async def _take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Создание скриншота экрана или региона"""
        save_path = params.get("save_path")
        region = params.get("region")
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                # PyAutoGUI скриншот
                if region:
                    screenshot = pyautogui.screenshot(
                        region=(region["x"], region["y"], region["width"], region["height"])
                    )
                else:
                    screenshot = pyautogui.screenshot()
                    
                # Сохранение
                if save_path:
                    screenshot.save(save_path)
                    file_size = os.path.getsize(save_path)
                else:
                    # Временный файл
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        screenshot.save(tmp.name)
                        save_path = tmp.name
                        file_size = os.path.getsize(save_path)
                
                return {
                    "success": True,
                    "screenshot_path": save_path,
                    "file_size": file_size,
                    "dimensions": screenshot.size,
                    "region": region,
                    "backend": "pyautogui"
                }
                
            elif self.backend == "x11_native":
                # X11 нативный скриншот через scrot
                if not save_path:
                    save_path = f"/tmp/kittycore_screenshot_{int(time.time())}.png"
                    
                if region:
                    cmd = f"scrot -a {region['x']},{region['y']},{region['width']},{region['height']} {save_path}"
                else:
                    cmd = f"scrot {save_path}"
                    
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(save_path):
                    file_size = os.path.getsize(save_path)
                    return {
                        "success": True,
                        "screenshot_path": save_path,
                        "file_size": file_size,
                        "region": region,
                        "backend": "x11_scrot"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"scrot ошибка: {result.stderr}",
                        "backend": "x11_scrot"
                    }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для скриншотов",
                    "available_backends": [self.backend],
                    "pyautogui_available": PYAUTOGUI_AVAILABLE
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка создания скриншота: {str(e)}",
                "backend": self.backend
            }
    
    async def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Клик мышью по координатам"""
        x = params.get("x")
        y = params.get("y") 
        button = params.get("button", "left")
        
        if x is None or y is None:
            return {
                "success": False,
                "error": "Требуются координаты x и y для клика"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                # PyAutoGUI клик
                if button == "left":
                    pyautogui.click(x, y)
                elif button == "right":
                    pyautogui.rightClick(x, y)
                elif button == "middle":
                    pyautogui.middleClick(x, y)
                    
                return {
                    "success": True,
                    "action": "click",
                    "coordinates": [x, y],
                    "button": button,
                    "backend": "pyautogui"
                }
                
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                # pynput клик
                mouse_controller = mouse.Controller()
                mouse_controller.position = (x, y)
                
                if button == "left":
                    mouse_controller.click(Button.left)
                elif button == "right":
                    mouse_controller.click(Button.right)
                elif button == "middle":
                    mouse_controller.click(Button.middle)
                    
                return {
                    "success": True,
                    "action": "click", 
                    "coordinates": [x, y],
                    "button": button,
                    "backend": "pynput"
                }
                
            elif self.backend == "x11_native":
                # X11 нативный клик через xdotool
                button_map = {"left": "1", "middle": "2", "right": "3"}
                button_num = button_map.get(button, "1")
                
                cmd = f"xdotool mousemove {x} {y} click {button_num}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "click",
                    "coordinates": [x, y], 
                    "button": button,
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для кликов",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка клика: {str(e)}",
                "coordinates": [x, y],
                "backend": self.backend
            }
    
    async def _type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ввод текста"""
        text = params.get("text")
        
        if not text:
            return {
                "success": False,
                "error": "Требуется параметр text для ввода"
            }
        
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                pyautogui.typewrite(text)
                return {
                    "success": True,
                    "action": "type_text",
                    "text_length": len(text),
                    "backend": "pyautogui"
                }
                
            elif self.backend == "pynput" and PYNPUT_AVAILABLE:
                keyboard_controller = keyboard.Controller()
                keyboard_controller.type(text)
                return {
                    "success": True,
                    "action": "type_text", 
                    "text_length": len(text),
                    "backend": "pynput"
                }
                
            elif self.backend == "x11_native":
                # X11 нативный ввод через xdotool
                cmd = f"xdotool type '{text}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "success": result.returncode == 0,
                    "action": "type_text",
                    "text_length": len(text), 
                    "backend": "x11_xdotool",
                    "error": result.stderr if result.returncode != 0 else None
                }
            else:
                return {
                    "success": False,
                    "error": "Нет доступного backend для ввода текста",
                    "backend": self.backend
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка ввода текста: {str(e)}",
                "backend": self.backend
            }

    def _detect_x11(self) -> bool:
        """Определяем работает ли X11"""
        try:
            return bool(os.environ.get("DISPLAY")) and self.env_info.is_linux
        except:
            return False

    def _detect_i3wm(self) -> bool:
        """Определяем используется ли i3 window manager"""
        try:
            result = subprocess.run(
                ["i3-msg", "-t", "get_version"], 
                capture_output=True, 
                text=True, 
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _init_backends(self) -> Dict[str, bool]:
        """Инициализируем доступные backends"""
        backends = {
            "pyautogui": PYAUTOGUI_AVAILABLE and self._test_pyautogui(),
            "pynput": PYNPUT_AVAILABLE,
            "opencv": OPENCV_AVAILABLE,
            "x11": X11_AVAILABLE and self._detect_x11(),
        }
        
        # Конфигурируем PyAutoGUI для Linux
        if backends["pyautogui"]:
            pyautogui.PAUSE = 0.1
            pyautogui.FAILSAFE = False
            # На Linux может потребоваться отключить fail-safe в углах для i3
            if self._detect_i3wm():
                pyautogui.FAILSAFE = False  # i3 часто имеет элементы в углах
        
        return backends

    def _test_pyautogui(self) -> bool:
        """Тестируем работоспособность PyAutoGUI"""
        try:
            # Простой тест - получение размера экрана
            width, height = pyautogui.size()
            return width > 0 and height > 0
        except Exception as e:
            print(f"⚠️ PyAutoGUI test failed: {e}")
            return False

    def _get_screen_info(self) -> ScreenInfo:
        """Получаем информацию о экране"""
        try:
            if self.backend == "pyautogui" and PYAUTOGUI_AVAILABLE:
                width, height = pyautogui.size()
                return ScreenInfo(
                    width=width,
                    height=height,
                    display_name=os.environ.get("DISPLAY", ":0")
                )
            elif self.backend == "x11" and self._detect_x11():
                disp = display.Display()
                screen = disp.screen()
                return ScreenInfo(
                    width=screen.width_in_pixels,
                    height=screen.height_in_pixels,
                    display_name=os.environ.get("DISPLAY", ":0")
                )
            else:
                # Fallback через xrandr
                result = subprocess.run(
                    ["xrandr", "--current"], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if ' connected primary ' in line or ' connected ' in line:
                            # Парсим строку типа "1920x1080+0+0"
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    resolution = part.split('+')[0]
                                    width, height = map(int, resolution.split('x'))
                                    return ScreenInfo(width=width, height=height)
                
                # Последний fallback
                return ScreenInfo(width=1920, height=1080)
                
        except Exception as e:
            print(f"⚠️ Не удалось определить размер экрана: {e}")
            return ScreenInfo(width=1920, height=1080)

    @property
    def name(self) -> str:
        return "computer_use"

    @property
    def description(self) -> str:
        return """
        Универсальный инструмент автоматизации GUI для взаимодействия с рабочим столом.
        
        Поддерживает:
        - Скриншоты экрана и поиск элементов
        - Клики мыши (левый, правый, двойной)
        - Движения и перетаскивание мыши
        - Ввод текста и нажатие клавиш
        - Прокрутка и жесты
        - Работа с окнами (i3wm интеграция)
        
        Оптимизирован для Manjaro Linux i3 X11.
        """ 