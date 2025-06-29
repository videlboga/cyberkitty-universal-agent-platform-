# Установочный скрипт для MVP приложения Smart Document Generator в Битрикс24

## Введение
Данный скрипт предназначен для установки MVP приложения "Smart Document Generator" в системе Битрикс24. Приложение позволяет автоматизировать процесс генерации документов с использованием AI-помощника и интеграции с CRM. Скрипт создает необходимые таблицы в базе данных, настраивает параметры и обеспечивает базовую функциональность приложения.

## Подготовка к установке
Перед запуском скрипта убедитесь, что:
1. У вас есть доступ к базе данных Битрикс24.
2. Установлен PHP версии 7.4 или выше.
3. Включены расширения PHP: `pdo_mysql`, `json`, `curl`.

## Структура скрипта
Скрипт состоит из следующих разделов:
1. Подключение к базе данных.
2. Создание таблиц.
3. Настройка параметров приложения.
4. Проверка успешной установки.

## Подключение к базе данных
Для подключения к базе данных используется PDO. Укажите параметры подключения в переменных `$host`, `$dbname`, `$user`, `$password`.