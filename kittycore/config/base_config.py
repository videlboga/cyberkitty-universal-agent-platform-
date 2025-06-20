"""
Config - Простая система конфигурации

Принципы:
- Environment variables + .env файлы
- Типизированные настройки
- Валидация значений
- Каскадная загрузка (env -> .env -> defaults)
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Основная конфигурация KittyCore"""
    
    # OpenRouter Settings (совместимо с OpenAI API)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    anthropic_api_key: Optional[str] = None  # Не используется
    default_model: str = "google/gemini-2.5-flash-preview-05-20:thinking"  # Gemini 2.5 Flash с thinking
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Database Settings  
    database_url: str = "sqlite:///kittycore.db"
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Agent Settings
    agent_timeout: int = 30
    max_memory_entries: int = 100
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_debug: bool = False
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """
        Создать конфигурацию из переменных окружения
        
        Args:
            env_file: Путь к .env файлу (опционально)
            
        Returns:
            Настроенная конфигурация
        """
        # Загружаем .env файл если указан
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        elif Path('.env').exists():
            load_dotenv('.env')
        
        return cls(
            # OpenRouter (совместимость с OPENAI_API_KEY)
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY'),
            openrouter_base_url=os.getenv('OPENROUTER_BASE_URL') or os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),  # Не используется
            default_model=os.getenv('DEFAULT_MODEL', 'google/gemini-2.5-flash-preview-05-20:thinking'),
            max_tokens=int(os.getenv('MAX_TOKENS', '1000')),
            temperature=float(os.getenv('TEMPERATURE', '0.7')),
            
            # Database
            database_url=os.getenv('DATABASE_URL', 'sqlite:///kittycore.db'),
            
            # Logging
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE'),
            
            # Agent
            agent_timeout=int(os.getenv('AGENT_TIMEOUT', '30')),
            max_memory_entries=int(os.getenv('MAX_MEMORY_ENTRIES', '100')),
            
            # API
            api_host=os.getenv('API_HOST', '0.0.0.0'),
            api_port=int(os.getenv('API_PORT', '8080')),
            api_debug=os.getenv('API_DEBUG', 'false').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Валидировать конфигурацию"""
        errors = []
        
        # Проверяем наличие API ключей
        if not self.openrouter_api_key and not self.anthropic_api_key:
            errors.append("Необходим хотя бы один API ключ (OpenRouter или Anthropic)")
        
        # Проверяем диапазоны значений
        if not 0 <= self.temperature <= 2:
            errors.append("Temperature должен быть между 0 и 2")
        
        if self.max_tokens <= 0:
            errors.append("Max tokens должен быть больше 0")
        
        if not 1024 <= self.api_port <= 65535:
            errors.append("API port должен быть между 1024 и 65535")
        
        if errors:
            print("❌ Ошибки конфигурации:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    # Свойства для обратной совместимости с OpenAI кодом
    @property 
    def openai_api_key(self) -> Optional[str]:
        """Совместимость: используем OpenRouter ключ"""
        return self.openrouter_api_key
    
    @property
    def openai_base_url(self) -> str:
        """Совместимость: используем OpenRouter URL"""
        return self.openrouter_base_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }


def load_dotenv(env_file: str) -> None:
    """
    Простая загрузка .env файла
    
    Заменяет python-dotenv для простых случаев
    """
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')
    except Exception:
        pass  # Игнорируем ошибки загрузки .env


# Глобальная конфигурация
_global_config = None


def get_config() -> Config:
    """Получить глобальную конфигурацию"""
    global _global_config
    if _global_config is None:
        _global_config = Config.from_env()
    return _global_config


def set_config(config: Config) -> None:
    """Установить глобальную конфигурацию"""
    global _global_config
    _global_config = config 