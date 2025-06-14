#!/usr/bin/env python3
"""
🎧 БЕНЧМАРК АГЕНТА ПОДДЕРЖКИ - ЧАСТЬ 1: БАЗА ЗНАНИЙ
Реалистичная имитация работы агента технической поддержки

СЦЕНАРИЙ: Агент поддержки интернет-провайдера "КиберКот"
- База знаний с решениями проблем
- Система тикетов и действий
- Эскалация сложных случаев
- Оценка качества обслуживания клиентов
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import time

class TicketPriority(Enum):
    """Приоритет тикета"""
    LOW = 1      # Низкий - общие вопросы
    MEDIUM = 2   # Средний - технические проблемы
    HIGH = 3     # Высокий - критические сбои
    URGENT = 4   # Срочный - массовые отключения

class TicketStatus(Enum):
    """Статус тикета"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ActionType(Enum):
    """Типы действий агента"""
    SEARCH_KB = "search_knowledge_base"      # Поиск в базе знаний
    RESTART_EQUIPMENT = "restart_equipment"   # Перезагрузка оборудования
    CHECK_CONNECTION = "check_connection"     # Проверка соединения
    ESCALATE = "escalate"                    # Эскалация
    SEND_TECHNICIAN = "send_technician"      # Отправка техника
    UPDATE_SETTINGS = "update_settings"      # Обновление настроек
    PROVIDE_INFO = "provide_information"     # Предоставление информации

@dataclass
class Customer:
    """Клиент"""
    id: str
    name: str
    plan: str  # Тарифный план
    location: str
    equipment: List[str]  # Оборудование клиента
    history: List[str]    # История обращений
    satisfaction_score: float = 5.0  # Оценка удовлетворённости

@dataclass
class KnowledgeBaseEntry:
    """Запись в базе знаний"""
    id: str
    title: str
    problem_keywords: List[str]
    solution_steps: List[str]
    required_actions: List[ActionType]
    escalation_needed: bool = False
    success_rate: float = 0.9

@dataclass
class SupportTicket:
    """Тикет поддержки"""
    id: str
    customer: Customer
    problem_description: str
    priority: TicketPriority
    status: TicketStatus
    created_at: float
    agent_actions: List[Dict[str, Any]]
    resolution_time: Optional[float] = None
    customer_satisfaction: Optional[float] = None

class KnowledgeBase:
    """База знаний техподдержки"""
    
    def __init__(self):
        self.entries = self._init_knowledge_base()
    
    def _init_knowledge_base(self) -> List[KnowledgeBaseEntry]:
        """Инициализация базы знаний"""
        return [
            # Проблемы с интернетом
            KnowledgeBaseEntry(
                id="kb_001",
                title="Нет интернета - базовая диагностика",
                problem_keywords=["нет интернета", "не работает", "отключился", "пропал"],
                solution_steps=[
                    "Проверить индикаторы на роутере",
                    "Перезагрузить роутер (выключить на 30 сек)",
                    "Проверить кабельные соединения",
                    "Проверить баланс лицевого счёта"
                ],
                required_actions=[ActionType.CHECK_CONNECTION, ActionType.RESTART_EQUIPMENT],
                success_rate=0.85
            ),
            KnowledgeBaseEntry(
                id="kb_002", 
                title="Медленный интернет",
                problem_keywords=["медленно", "тормозит", "низкая скорость", "долго загружается"],
                solution_steps=[
                    "Проверить скорость через speedtest",
                    "Отключить лишние устройства",
                    "Проверить настройки Wi-Fi канала",
                    "Обновить драйверы сетевой карты"
                ],
                required_actions=[ActionType.CHECK_CONNECTION, ActionType.UPDATE_SETTINGS],
                success_rate=0.75
            ),
            
            # Проблемы с оборудованием
            KnowledgeBaseEntry(
                id="kb_003",
                title="Роутер не включается",
                problem_keywords=["не включается", "не горят лампочки", "мёртвый", "сломался"],
                solution_steps=[
                    "Проверить подключение питания",
                    "Попробовать другую розетку",
                    "Проверить блок питания",
                    "Если не помогает - замена оборудования"
                ],
                required_actions=[ActionType.RESTART_EQUIPMENT, ActionType.SEND_TECHNICIAN],
                escalation_needed=True,
                success_rate=0.6
            ),
            
            # Настройки и конфигурация
            KnowledgeBaseEntry(
                id="kb_004",
                title="Настройка Wi-Fi пароля",
                problem_keywords=["пароль wifi", "изменить пароль", "забыл пароль", "настройка wifi"],
                solution_steps=[
                    "Зайти в веб-интерфейс роутера (192.168.1.1)",
                    "Ввести логин/пароль (admin/admin)",
                    "Перейти в раздел Wi-Fi настройки",
                    "Изменить пароль (минимум 8 символов)"
                ],
                required_actions=[ActionType.UPDATE_SETTINGS, ActionType.PROVIDE_INFO],
                success_rate=0.95
            ),
            
            # Биллинг и тарифы
            KnowledgeBaseEntry(
                id="kb_005",
                title="Вопросы по тарифу и оплате",
                problem_keywords=["тариф", "оплата", "баланс", "счёт", "деньги"],
                solution_steps=[
                    "Проверить текущий баланс в личном кабинете",
                    "Объяснить условия тарифного плана",
                    "Предложить способы пополнения",
                    "При необходимости - смена тарифа"
                ],
                required_actions=[ActionType.PROVIDE_INFO],
                success_rate=0.9
            ),
            
            # Нестандартные ситуации
            KnowledgeBaseEntry(
                id="kb_006",
                title="Массовые отключения в районе",
                problem_keywords=["у всех не работает", "в районе отключили", "авария", "массовый сбой"],
                solution_steps=[
                    "Проверить карту аварий",
                    "Уведомить о плановых работах",
                    "Дать примерное время восстановления",
                    "Предложить компенсацию при длительном сбое"
                ],
                required_actions=[ActionType.ESCALATE, ActionType.PROVIDE_INFO],
                escalation_needed=True,
                success_rate=0.7
            )
        ]
    
    def search(self, query: str) -> List[KnowledgeBaseEntry]:
        """Поиск в базе знаний"""
        query_lower = query.lower()
        results = []
        
        for entry in self.entries:
            # Проверяем совпадения с ключевыми словами
            for keyword in entry.problem_keywords:
                if keyword in query_lower:
                    results.append(entry)
                    break
        
        # Сортируем по успешности решения
        return sorted(results, key=lambda x: x.success_rate, reverse=True)

class CustomerDatabase:
    """База данных клиентов"""
    
    def __init__(self):
        self.customers = self._init_customers()
    
    def _init_customers(self) -> Dict[str, Customer]:
        """Инициализация базы клиентов"""
        return {
            "cust_001": Customer(
                id="cust_001",
                name="Анна Петрова",
                plan="Домашний 100 Мбит/с",
                location="ул. Ленина, 15, кв. 42",
                equipment=["Роутер TP-Link", "ONT Huawei"],
                history=["Настройка Wi-Fi (2024-01-15)", "Медленный интернет (2024-02-20)"],
                satisfaction_score=4.2
            ),
            "cust_002": Customer(
                id="cust_002", 
                name="Иван Сидоров",
                plan="Бизнес 500 Мбит/с",
                location="пр. Мира, 88, офис 12",
                equipment=["Роутер Cisco", "Коммутатор D-Link"],
                history=["Установка (2023-12-01)"],
                satisfaction_score=4.8
            ),
            "cust_003": Customer(
                id="cust_003",
                name="Мария Козлова", 
                plan="Базовый 50 Мбит/с",
                location="ул. Садовая, 7, кв. 5",
                equipment=["Роутер Keenetic"],
                history=["Частые отключения (2024-01-10)", "Замена роутера (2024-01-25)", "Нет интернета (2024-03-01)"],
                satisfaction_score=2.1  # Недовольный клиент
            )
        }
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Получить клиента по ID"""
        return self.customers.get(customer_id)

# Демонстрация базы знаний
if __name__ == "__main__":
    print("🎧 БЕНЧМАРК АГЕНТА ПОДДЕРЖКИ - БАЗА ЗНАНИЙ")
    print("=" * 60)
    
    kb = KnowledgeBase()
    customers = CustomerDatabase()
    
    print(f"\n📚 БАЗА ЗНАНИЙ ({len(kb.entries)} записей):")
    for entry in kb.entries:
        print(f"  • {entry.title}")
        print(f"    Ключевые слова: {', '.join(entry.problem_keywords[:3])}...")
        print(f"    Успешность: {entry.success_rate*100:.0f}%")
        if entry.escalation_needed:
            print(f"    ⚠️ Требует эскалации")
        print()
    
    print(f"👥 БАЗА КЛИЕНТОВ ({len(customers.customers)} клиентов):")
    for customer in customers.customers.values():
        print(f"  • {customer.name} ({customer.plan})")
        print(f"    Удовлетворённость: {customer.satisfaction_score}/5.0")
        print(f"    История: {len(customer.history)} обращений")
        print()
    
    print("🔍 ТЕСТ ПОИСКА:")
    test_queries = ["нет интернета", "медленно работает", "пароль wifi"]
    
    for query in test_queries:
        results = kb.search(query)
        print(f"\nЗапрос: '{query}'")
        print(f"Найдено: {len(results)} решений")
        for result in results[:2]:  # Показываем топ-2
            print(f"  → {result.title} (успех: {result.success_rate*100:.0f}%)")
    
    print("\n✅ База знаний готова!")
    print("🔄 Следующий шаг: создание системы тикетов и агента...") 