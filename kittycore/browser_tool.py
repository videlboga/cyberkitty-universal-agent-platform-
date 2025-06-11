"""
BrowserTool - Мощный веб движок для KittyCore агентов
Полная автоматизация браузера с обходом капчи и anti-bot систем

Возможности:
- Playwright/Selenium автоматизация
- Обход капчи (2captcha, anti-captcha)
- Стелс режим (anti-detection)
- Прокси и ротация User-Agent
- Cookie/Session менеджмент
- Скриншоты и PDF
- Форм автозаполнение
"""

import asyncio
import os
import sys
import json
import time
import random
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging

from .tools import Tool, ToolResult

logger = logging.getLogger(__name__)

# Проверяем доступность библиотек
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


@dataclass
class BrowserConfig:
    """Конфигурация браузера"""
    engine: str = "playwright"  # playwright, selenium
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    stealth_mode: bool = True
    anti_detection: bool = True
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = None
    timeout: int = 30000
    captcha_service: Optional[str] = None  # 2captcha, anti-captcha
    captcha_api_key: Optional[str] = None


class BrowserTool(Tool):
    """
    Универсальный браузер инструмент для агентов
    Объединяет Playwright, Selenium, анти-детект и обход капчи
    """
    
    def __init__(self, config: BrowserConfig = None):
        super().__init__(
            name="browser",
            description="Полная автоматизация веб-браузера с обходом защит"
        )
        
        self.config = config or BrowserConfig()
        self.browser = None
        self.page = None
        self.context = None
        self.session_data = {}
        
        # Стелс конфигурация
        self.stealth_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # User-Agent pool для ротации
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
    
    def get_schema(self):
        """Схема для браузерных операций"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        # Основные операции
                        "navigate", "click", "type", "submit", "scroll",
                        # Извлечение данных
                        "get_text", "get_attribute", "get_html", "screenshot",
                        # Ожидание
                        "wait_for_element", "wait_for_text", "wait_for_url",
                        # Формы и инпуты
                        "fill_form", "select_option", "upload_file",
                        # Управление сессией
                        "set_cookies", "get_cookies", "clear_cookies",
                        # Прокси и стелс
                        "set_proxy", "rotate_user_agent", "stealth_mode",
                        # Капча
                        "solve_captcha", "bypass_protection",
                        # Утилиты
                        "pdf_save", "evaluate_js", "network_log"
                    ],
                    "description": "Действие для выполнения"
                },
                "url": {
                    "type": "string",
                    "description": "URL для навигации"
                },
                "selector": {
                    "type": "string", 
                    "description": "CSS селектор элемента"
                },
                "text": {
                    "type": "string",
                    "description": "Текст для ввода"
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут в миллисекундах"
                },
                "options": {
                    "type": "object",
                    "description": "Дополнительные опции"
                }
            },
            "required": ["action"]
        }
    
    def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнить браузерную операцию"""
        if not PLAYWRIGHT_AVAILABLE and not SELENIUM_AVAILABLE:
            return ToolResult(
                success=False,
                error="Ни Playwright, ни Selenium не установлены. Установите: pip install playwright selenium"
            )
        
        try:
            # Запускаем асинхронную операцию
            if self.config.engine == "playwright" and PLAYWRIGHT_AVAILABLE:
                result = asyncio.run(self._execute_playwright(action, **kwargs))
            elif self.config.engine == "selenium" and SELENIUM_AVAILABLE:
                result = self._execute_selenium(action, **kwargs)
            else:
                # Fallback на доступный движок
                if PLAYWRIGHT_AVAILABLE:
                    result = asyncio.run(self._execute_playwright(action, **kwargs))
                elif SELENIUM_AVAILABLE:
                    result = self._execute_selenium(action, **kwargs)
                else:
                    return ToolResult(success=False, error="Нет доступных браузерных движков")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка браузерной операции {action}: {e}")
            return ToolResult(success=False, error=str(e))
    
    async def _execute_playwright(self, action: str, **kwargs) -> ToolResult:
        """Асинхронное выполнение через Playwright"""
        
        # Инициализация браузера если нужно
        if not self.browser:
            await self._init_playwright_browser()
        
        if action == "navigate":
            return await self._playwright_navigate(**kwargs)
        elif action == "click":
            return await self._playwright_click(**kwargs)
        elif action == "type":
            return await self._playwright_type(**kwargs)
        elif action == "get_text":
            return await self._playwright_get_text(**kwargs)
        elif action == "screenshot":
            return await self._playwright_screenshot(**kwargs)
        elif action == "wait_for_element":
            return await self._playwright_wait_for_element(**kwargs)
        elif action == "solve_captcha":
            return await self._playwright_solve_captcha(**kwargs)
        elif action == "stealth_mode":
            return await self._playwright_stealth_mode(**kwargs)
        else:
            return ToolResult(success=False, error=f"Неизвестное действие: {action}")
    
    def _execute_selenium(self, action: str, **kwargs) -> ToolResult:
        """Синхронное выполнение через Selenium"""
        
        # Инициализация браузера если нужно
        if not self.browser:
            self._init_selenium_browser()
        
        if action == "navigate":
            return self._selenium_navigate(**kwargs)
        elif action == "click":
            return self._selenium_click(**kwargs)
        elif action == "type":
            return self._selenium_type(**kwargs)
        elif action == "get_text":
            return self._selenium_get_text(**kwargs)
        elif action == "screenshot":
            return self._selenium_screenshot(**kwargs)
        else:
            return ToolResult(success=False, error=f"Неизвестное действие: {action}")
    
    # =====================================================
    # ИНИЦИАЛИЗАЦИЯ БРАУЗЕРОВ
    # =====================================================
    
    async def _init_playwright_browser(self):
        """Инициализация Playwright браузера"""
        try:
            self.playwright = await async_playwright().start()
            
            # Настройки запуска браузера
            launch_options = {
                "headless": self.config.headless,
                "args": []
            }
            
            # Анти-детект настройки
            if self.config.anti_detection:
                launch_options["args"].extend([
                    "--no-first-run",
                    "--no-default-browser-check", 
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--exclude-switches=enable-automation",
                    "--disable-extensions-file-access-check",
                    "--disable-extensions-http-throttling",
                    "--disable-extensions-https-throttling"
                ])
            
            # Запуск браузера
            if self.config.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(**launch_options)
            elif self.config.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(**launch_options)
            elif self.config.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(**launch_options)
            
            # Создание контекста с настройками
            context_options = {}
            
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
            else:
                context_options["user_agent"] = random.choice(self.user_agents)
            
            if self.config.viewport:
                context_options["viewport"] = self.config.viewport
            else:
                context_options["viewport"] = {"width": 1920, "height": 1080}
            
            # Прокси
            if self.config.proxy:
                context_options["proxy"] = {"server": self.config.proxy}
            
            self.context = await self.browser.new_context(**context_options)
            
            # Стелс настройки
            if self.config.stealth_mode:
                await self._apply_stealth_settings()
            
            # Создание страницы
            self.page = await self.context.new_page()
            
            logger.info("Playwright браузер инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Playwright: {e}")
            raise
    
    def _init_selenium_browser(self):
        """Инициализация Selenium браузера"""
        try:
            if self.config.browser_type == "chromium":
                options = ChromeOptions()
                
                if self.config.headless:
                    options.add_argument("--headless")
                
                # Анти-детект настройки
                if self.config.anti_detection:
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                
                # User-Agent
                if self.config.user_agent:
                    options.add_argument(f"--user-agent={self.config.user_agent}")
                else:
                    options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
                
                # Прокси
                if self.config.proxy:
                    options.add_argument(f"--proxy-server={self.config.proxy}")
                
                self.browser = webdriver.Chrome(options=options)
                
            elif self.config.browser_type == "firefox":
                options = FirefoxOptions()
                
                if self.config.headless:
                    options.add_argument("--headless")
                
                if self.config.user_agent:
                    options.set_preference("general.useragent.override", self.config.user_agent)
                
                self.browser = webdriver.Firefox(options=options)
            
            # Настройки окна
            if self.config.viewport:
                self.browser.set_window_size(
                    self.config.viewport["width"], 
                    self.config.viewport["height"]
                )
            else:
                self.browser.set_window_size(1920, 1080)
            
            logger.info("Selenium браузер инициализирован")
            
                 except Exception as e:
             logger.error(f"Ошибка инициализации Selenium: {e}")
             raise
    
    # =====================================================
    # PLAYWRIGHT МЕТОДЫ - ОСНОВНЫЕ ОПЕРАЦИИ
    # =====================================================
    
    async def _apply_stealth_settings(self):
        """Применение стелс настроек для обхода детекции"""
        if not self.context:
            return
        
        # Скрываем webdriver свойства
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Переопределяем plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Переопределяем языки
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Переопределяем permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Подменяем chrome объект
            window.chrome = {
                runtime: {},
            };
        """)

    async def _playwright_navigate(self, **kwargs) -> ToolResult:
        """Навигация по URL"""
        try:
            url = kwargs.get("url")
            timeout = kwargs.get("timeout", self.config.timeout)
            
            if not url:
                return ToolResult(success=False, error="URL обязателен для навигации")
            
            # Добавляем случайную задержку для имитации человека
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            response = await self.page.goto(url, timeout=timeout)
            
            result_data = {
                "url": self.page.url,
                "title": await self.page.title(),
                "status": response.status if response else None,
                "loaded": True
            }
            
            return ToolResult(success=True, data=result_data)
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка навигации: {e}")

    async def _playwright_click(self, **kwargs) -> ToolResult:
        """Клик по элементу"""
        try:
            selector = kwargs.get("selector")
            timeout = kwargs.get("timeout", self.config.timeout)
            
            if not selector:
                return ToolResult(success=False, error="Селектор обязателен для клика")
            
            # Ждем элемент
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            # Скроллим к элементу
            await self.page.locator(selector).scroll_into_view_if_needed()
            
            # Добавляем человеческую задержку
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Кликаем
            await self.page.click(selector)
            
            return ToolResult(
                success=True,
                data={
                    "selector": selector,
                    "action": "clicked",
                    "url": self.page.url
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка клика: {e}")

    async def _playwright_type(self, **kwargs) -> ToolResult:
        """Ввод текста в элемент"""
        try:
            selector = kwargs.get("selector")
            text = kwargs.get("text", "")
            timeout = kwargs.get("timeout", self.config.timeout)
            delay = kwargs.get("delay", random.randint(50, 150))  # Имитация человеческого ввода
            
            if not selector:
                return ToolResult(success=False, error="Селектор обязателен для ввода")
            
            # Ждем элемент
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            # Очищаем поле
            await self.page.fill(selector, "")
            
            # Имитируем человеческий ввод
            await self.page.type(selector, text, delay=delay)
            
            return ToolResult(
                success=True,
                data={
                    "selector": selector,
                    "text": text,
                    "action": "typed",
                    "url": self.page.url
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка ввода: {e}")

    async def _playwright_get_text(self, **kwargs) -> ToolResult:
        """Получение текста элемента"""
        try:
            selector = kwargs.get("selector")
            timeout = kwargs.get("timeout", self.config.timeout)
            
            if not selector:
                return ToolResult(success=False, error="Селектор обязателен для получения текста")
            
            # Ждем элемент
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            # Получаем текст
            text = await self.page.text_content(selector)
            
            return ToolResult(
                success=True,
                data={
                    "selector": selector,
                    "text": text,
                    "url": self.page.url
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка получения текста: {e}")

    async def _playwright_screenshot(self, **kwargs) -> ToolResult:
        """Создание скриншота"""
        try:
            file_path = kwargs.get("file_path", f"screenshot_{int(time.time())}.png")
            full_page = kwargs.get("full_page", False)
            
            # Создаем скриншот
            screenshot_data = await self.page.screenshot(
                path=file_path,
                full_page=full_page
            )
            
            # Также возвращаем base64 для удобства
            screenshot_base64 = base64.b64encode(screenshot_data).decode()
            
            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "screenshot_base64": screenshot_base64,
                    "url": self.page.url,
                    "title": await self.page.title()
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка скриншота: {e}")

    async def _playwright_wait_for_element(self, **kwargs) -> ToolResult:
        """Ожидание появления элемента"""
        try:
            selector = kwargs.get("selector")
            timeout = kwargs.get("timeout", self.config.timeout)
            state = kwargs.get("state", "visible")  # visible, attached, detached, hidden
            
            if not selector:
                return ToolResult(success=False, error="Селектор обязателен для ожидания")
            
            # Ждем элемент
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            
            # Получаем информацию об элементе
            element = self.page.locator(selector)
            is_visible = await element.is_visible()
            is_enabled = await element.is_enabled()
            
            return ToolResult(
                success=True,
                data={
                    "selector": selector,
                    "state": state,
                    "is_visible": is_visible,
                    "is_enabled": is_enabled,
                    "found": True
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Элемент не найден: {e}")

    # =====================================================
    # ОБХОД КАПЧИ И ANTI-BOT СИСТЕМ
    # =====================================================

    class CaptchaSolver:
        """Универсальный решатель капчи"""
        
        def __init__(self, service="2captcha", api_key=None):
            self.service = service
            self.api_key = api_key
            self.session = None
        
        async def init_session(self):
            """Инициализация сессии для API капчи"""
            if not self.session and HTTP_AVAILABLE:
                import aiohttp
                self.session = aiohttp.ClientSession()
        
        async def solve_recaptcha_v2(self, site_key, page_url):
            """Решение reCAPTCHA v2"""
            if self.service == "2captcha":
                return await self._solve_2captcha_recaptcha_v2(site_key, page_url)
            else:
                raise ValueError(f"Неизвестный сервис капчи: {self.service}")
        
        async def _solve_2captcha_recaptcha_v2(self, site_key, page_url):
            """Решение reCAPTCHA v2 через 2captcha"""
            await self.init_session()
            
            # Отправляем задачу
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            async with self.session.post(submit_url, data=submit_data) as resp:
                result = await resp.json()
                
            if result['status'] != 1:
                raise Exception(f"Ошибка отправки капчи: {result.get('error_text', 'Unknown error')}")
            
            task_id = result['request']
            
            # Ждем решение
            result_url = "http://2captcha.com/res.php"
            
            for _ in range(60):  # Ждем до 5 минут
                await asyncio.sleep(5)
                
                async with self.session.get(result_url, params={
                    'key': self.api_key,
                    'action': 'get',
                    'id': task_id,
                    'json': 1
                }) as resp:
                    result = await resp.json()
                
                if result['status'] == 1:
                    return result['request']
                elif result['request'] != 'CAPCHA_NOT_READY':
                    raise Exception(f"Ошибка решения капчи: {result.get('request', 'Unknown error')}")
            
            raise Exception("Таймаут решения капчи")

    async def _playwright_solve_captcha(self, **kwargs) -> ToolResult:
        """Универсальное решение капчи"""
        try:
            captcha_type = kwargs.get("captcha_type", "auto")
            
            if not self.config.captcha_api_key:
                return ToolResult(success=False, error="API ключ капчи не настроен")
            
            # Автоопределение типа капчи если нужно
            if captcha_type == "auto":
                captcha_type = await self._detect_captcha_type()
            
            if captcha_type == "none":
                return ToolResult(success=True, data={"message": "Капча не обнаружена"})
            
            solver = self.CaptchaSolver(self.config.captcha_service, self.config.captcha_api_key)
            
            if captcha_type == "recaptcha_v2":
                return await self._solve_recaptcha_v2(solver, **kwargs)
            else:
                return ToolResult(success=False, error=f"Неподдерживаемый тип капчи: {captcha_type}")
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка решения капчи: {e}")

    async def _detect_captcha_type(self):
        """Автоматическое определение типа капчи на странице"""
        try:
            # Проверяем reCAPTCHA v2
            recaptcha_v2 = await self.page.query_selector('.g-recaptcha')
            if recaptcha_v2:
                return "recaptcha_v2"
            
            return "none"
            
        except Exception:
            return "none"

    async def _solve_recaptcha_v2(self, solver, **kwargs):
        """Решение reCAPTCHA v2"""
        try:
            # Получаем site key
            site_key = await self.page.evaluate("""
                () => {
                    const element = document.querySelector('.g-recaptcha');
                    return element ? element.getAttribute('data-sitekey') : null;
                }
            """)
            
            if not site_key:
                return ToolResult(success=False, error="Site key для reCAPTCHA v2 не найден")
            
            # Решаем капчу
            token = await solver.solve_recaptcha_v2(site_key, self.page.url)
            
            # Вставляем токен
            await self.page.evaluate(f"""
                () => {{
                    const textarea = document.querySelector('#g-recaptcha-response');
                    if (textarea) {{
                        textarea.style.display = 'block';
                        textarea.value = '{token}';
                        textarea.dispatchEvent(new Event('change'));
                    }}
                }}
            """)
            
            return ToolResult(
                success=True,
                data={
                    "captcha_type": "recaptcha_v2",
                    "token": token,
                    "solved": True
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка решения reCAPTCHA v2: {e}")

    async def _playwright_stealth_mode(self, **kwargs) -> ToolResult:
        """Активация продвинутого стелс режима"""
        try:
            # Дополнительные стелс скрипты
            await self.context.add_init_script("""
                // Убираем следы автоматизации
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Подделываем battery API
                Object.defineProperty(navigator, 'getBattery', {
                    value: () => Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1
                    })
                });
                
                // Подделываем connection
                Object.defineProperty(navigator, 'connection', {
                    value: {
                        downlink: 10,
                        effectiveType: '4g',
                        rtt: 50,
                        saveData: false
                    }
                });
            """)
            
            return ToolResult(
                success=True,
                data={
                    "stealth_mode": True,
                    "message": "Продвинутый стелс режим активирован"
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Ошибка активации стелс режима: {e}")

    # =====================================================
    # SELENIUM МЕТОДЫ (УПРОЩЕННЫЕ)
    # =====================================================

    def _selenium_navigate(self, **kwargs) -> ToolResult:
        """Selenium навигация"""
        try:
            url = kwargs.get("url")
            if not url:
                return ToolResult(success=False, error="URL обязателен")
            
            self.browser.get(url)
            
            return ToolResult(
                success=True,
                data={
                    "url": self.browser.current_url,
                    "title": self.browser.title
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Selenium навигация: {e}")

    def _selenium_click(self, **kwargs) -> ToolResult:
        """Selenium клик"""
        try:
            selector = kwargs.get("selector")
            timeout = kwargs.get("timeout", 30)
            
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            
            return ToolResult(success=True, data={"clicked": selector})
        except Exception as e:
            return ToolResult(success=False, error=f"Selenium клик: {e}")

    def _selenium_type(self, **kwargs) -> ToolResult:
        """Selenium ввод текста"""
        try:
            selector = kwargs.get("selector")
            text = kwargs.get("text", "")
            timeout = kwargs.get("timeout", 30)
            
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            
            return ToolResult(success=True, data={"typed": text})
        except Exception as e:
            return ToolResult(success=False, error=f"Selenium ввод: {e}")

    def _selenium_get_text(self, **kwargs) -> ToolResult:
        """Selenium получение текста"""
        try:
            selector = kwargs.get("selector")
            timeout = kwargs.get("timeout", 30)
            
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            return ToolResult(success=True, data={"text": element.text})
        except Exception as e:
            return ToolResult(success=False, error=f"Selenium текст: {e}")

    def _selenium_screenshot(self, **kwargs) -> ToolResult:
        """Selenium скриншот"""
        try:
            file_path = kwargs.get("file_path", f"selenium_screenshot_{int(time.time())}.png")
            
            self.browser.save_screenshot(file_path)
            
            return ToolResult(success=True, data={"screenshot": file_path})
        except Exception as e:
            return ToolResult(success=False, error=f"Selenium скриншот: {e}")

    # =====================================================
    # CLEANUP И LIFECYCLE
    # =====================================================

    async def close(self):
        """Закрытие браузера и очистка ресурсов"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Ошибка закрытия браузера: {e}")

    def __del__(self):
        """Деструктор"""
        if hasattr(self, 'browser') and self.browser:
            try:
                if self.config.engine == "selenium":
                    self.browser.quit()
            except Exception:
                pass 