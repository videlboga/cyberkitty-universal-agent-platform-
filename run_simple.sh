#!/bin/bash

# Скрипт запуска упрощенной архитектуры Universal Agent Platform в Docker

set -e

echo "🚀 Запуск Universal Agent Platform - Simplified Architecture"
echo "============================================================="

# Проверяем что Docker доступен
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не найден. Установите docker-compose и попробуйте снова."
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Останавливаем старые контейнеры (если есть)
echo "🛑 Останавливаем старые контейнеры..."
docker-compose -f docker-compose.simple.yml down --remove-orphans || true

# Собираем образ
echo "🔨 Сборка Docker образа..."
docker-compose -f docker-compose.simple.yml build

# Запускаем сервисы
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.simple.yml up -d

# Ждем запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверяем статус
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.simple.yml ps

# Показываем логи
echo ""
echo "📋 Последние логи сервера:"
docker-compose -f docker-compose.simple.yml logs --tail=20 app_simple

echo ""
echo "✅ Упрощенная архитектура запущена!"
echo "🌐 API доступно по адресу: http://localhost:8080"
echo "📚 Документация: http://localhost:8080/docs"
echo "💚 Health check: http://localhost:8080/simple/health"
echo "📋 Информация: http://localhost:8080/simple/info"
echo ""
echo "🔧 Полезные команды:"
echo "  Просмотр логов:     docker-compose -f docker-compose.simple.yml logs -f app_simple"
echo "  Остановка:          docker-compose -f docker-compose.simple.yml down"
echo "  Запуск тестов:      python test_simple_api_http.py"
echo ""
echo "🎯 Готово для тестирования!" 