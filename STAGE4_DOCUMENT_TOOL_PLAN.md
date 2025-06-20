# 📄 ЭТАП 4: Разделение DocumentTool - ПЛАН

## 🎯 Цель ЭТАПА 4
Разделить монолитный `document_tool.py` (2100 строк, 23 класса) на логические модули для улучшения архитектуры и поддерживаемости.

## 📊 Анализ текущего состояния

**ПРОБЛЕМА:**
- ❌ 2100 строк в одном файле
- ❌ 23 класса смешаны в одном модуле
- ❌ Сложное тестирование и отладка
- ❌ Нарушение принципа Single Responsibility
- ❌ Дублирование кода между процессорами

## 🏗️ Архитектура разделения

### 📁 Планируемая структура модулей

```
document_tools/
├── document_common.py          # Общие структуры и утилиты
│   ├── DocumentFormat (Enum)
│   ├── ProcessingStrategy (Enum)  
│   ├── DocumentMetadata
│   ├── ExtractionResult
│   ├── DocumentUtils
│   └── DocumentFormatDetector
│
├── document_processors/        # Базовые процессоры
│   ├── base_processor.py
│   │   └── DocumentProcessor (базовый класс)
│   │
│   ├── text_processor.py
│   │   └── TextProcessor
│   │
│   ├── pdf_processor.py
│   │   └── PDFProcessor
│   │
│   ├── docx_processor.py
│   │   └── DOCXProcessor
│   │
│   ├── csv_processor.py
│   │   └── CSVProcessor
│   │
│   ├── json_processor.py
│   │   └── JSONProcessor
│   │
│   ├── xml_processor.py
│   │   └── XMLProcessor
│   │
│   └── image_processor.py
│       └── ImageProcessor
│
├── ocr_engines/               # OCR движки
│   ├── ocr_common.py
│   │   ├── OCREngine (Enum)
│   │   ├── OCRResult
│   │   └── BaseOCRProcessor
│   │
│   ├── tesseract_ocr.py
│   │   └── TesseractOCRProcessor
│   │
│   ├── easyocr_processor.py
│   │   └── EasyOCRProcessor
│   │
│   ├── multimodal_llm_ocr.py
│   │   └── MultimodalLLMOCRProcessor
│   │
│   └── ocr_orchestrator.py
│       └── OCROrchestrator
│
├── document_orchestrator.py    # Главный оркестратор
│   └── DocumentOrchestrator
│
└── document_tool.py           # Unified интерфейс
    └── DocumentTool (основной класс)
```

## 📋 Детальный план создания файлов

### 1️⃣ document_common.py (~300 строк)
**Содержимое:**
- `DocumentFormat` (Enum) - форматы документов
- `ProcessingStrategy` (Enum) - стратегии обработки  
- `DocumentMetadata` (dataclass) - метаданные документа
- `ExtractionResult` (dataclass) - результат извлечения
- `DocumentUtils` (класс) - утилиты (checksum, encoding, etc.)
- `DocumentFormatDetector` (класс) - определение форматов

### 2️⃣ document_processors/base_processor.py (~100 строк)
**Содержимое:**
- `DocumentProcessor` (базовый класс)
- Общие методы валидации и обработки
- Абстрактные методы для наследников

### 3️⃣ document_processors/pdf_processor.py (~200 строк)
**Содержимое:**
- `PDFProcessor` (класс)
- Поддержка: PyMuPDF, pdfplumber, pdfminer, PyPDF2
- Извлечение текста, таблиц, изображений

### 4️⃣ document_processors/docx_processor.py (~150 строк)
**Содержимое:**
- `DOCXProcessor` (класс)
- Работа с python-docx
- Извлечение текста, таблиц, изображений

### 5️⃣ document_processors/text_processor.py (~100 строк)
**Содержимое:**
- `TextProcessor` (класс)
- Обработка TXT файлов
- Определение кодировки

### 6️⃣ document_processors/csv_processor.py (~150 строк)
**Содержимое:**
- `CSVProcessor` (класс)
- Обработка CSV файлов
- Различные разделители и кодировки

### 7️⃣ document_processors/json_processor.py (~120 строк)
**Содержимое:**
- `JSONProcessor` (класс)
- Обработка JSON файлов
- Преобразование в читаемый текст

### 8️⃣ document_processors/xml_processor.py (~150 строк)
**Содержимое:**
- `XMLProcessor` (класс)
- Обработка XML и HTML файлов
- BeautifulSoup интеграция

### 9️⃣ document_processors/image_processor.py (~120 строк)
**Содержимое:**
- `ImageProcessor` (класс)
- Обработка изображений
- Извлечение метаданных

### 🔟 ocr_engines/ocr_common.py (~150 строк)
**Содержимое:**
- `OCREngine` (Enum) - движки OCR
- `OCRResult` (dataclass) - результат OCR
- `BaseOCRProcessor` (класс) - базовый OCR процессор

### 1️⃣1️⃣ ocr_engines/tesseract_ocr.py (~200 строк)
**Содержимое:**
- `TesseractOCRProcessor` (класс)
- Интеграция с Tesseract
- Поддержка множественных языков

### 1️⃣2️⃣ ocr_engines/easyocr_processor.py (~150 строк)
**Содержимое:**
- `EasyOCRProcessor` (класс)
- Deep learning OCR
- Автоматическое определение языка

### 1️⃣3️⃣ ocr_engines/multimodal_llm_ocr.py (~200 строк)
**Содержимое:**
- `MultimodalLLMOCRProcessor` (класс)
- GPT-4V, Claude 3 интеграция
- Облачные OCR сервисы

### 1️⃣4️⃣ ocr_engines/ocr_orchestrator.py (~150 строк)
**Содержимое:**
- `OCROrchestrator` (класс)
- Выбор лучшего OCR движка
- Комбинирование результатов

### 1️⃣5️⃣ document_orchestrator.py (~200 строк)
**Содержимое:**
- `DocumentOrchestrator` (класс)
- Основная логика обработки документов
- Выбор процессоров и стратегий

### 1️⃣6️⃣ document_tool.py (~150 строк)
**Содержимое:**
- `DocumentTool` (основной класс)
- Unified интерфейс для всех модулей
- Обратная совместимость

## 📊 Ожидаемые результаты

### ✅ Экономия строк кода
- **БЫЛО:** 1 файл (2100 строк)
- **СТАНЕТ:** 16 файлов (~2300 строк всего)
- **ЭКОНОМИЯ:** 2100 - 150 (unified) = **1950 строк экономии**

### ✅ Качественные улучшения
- 🔧 **Модульность:** каждый процессор независим
- 🧪 **Тестируемость:** изолированное тестирование компонентов  
- 📈 **Масштабируемость:** простое добавление новых форматов
- 🔄 **Переиспользование:** общие компоненты в document_common
- 🛡️ **Надёжность:** изолированные зависимости

### ✅ Архитектурные преимущества
- **Single Responsibility:** каждый класс одна задача
- **Open/Closed:** легко расширять без изменения существующего
- **Dependency Inversion:** зависимости через интерфейсы
- **DRY:** общий код вынесен в базовые классы

## 🚀 План выполнения

### Этап 4.1: Общие компоненты
1. Создать `document_common.py`
2. Создать `document_processors/base_processor.py`
3. Создать `ocr_engines/ocr_common.py`

### Этап 4.2: Основные процессоры
4. Создать `pdf_processor.py` 
5. Создать `docx_processor.py`
6. Создать `text_processor.py`
7. Создать `csv_processor.py`

### Этап 4.3: Дополнительные процессоры
8. Создать `json_processor.py`
9. Создать `xml_processor.py`
10. Создать `image_processor.py`

### Этап 4.4: OCR движки
11. Создать `tesseract_ocr.py`
12. Создать `easyocr_processor.py`  
13. Создать `multimodal_llm_ocr.py`
14. Создать `ocr_orchestrator.py`

### Этап 4.5: Оркестраторы
15. Создать `document_orchestrator.py`
16. Создать unified `document_tool.py`

### Этап 4.6: Тестирование и проверка
17. Проверить синтаксис всех файлов
18. Проверить импорты и зависимости
19. Провести smoke test
20. Создать отчёт

## 🎯 Критерии успеха

- ✅ Все 23 класса разделены по логическим модулям
- ✅ 100% обратная совместимость
- ✅ Синтаксис всех файлов проходит проверку
- ✅ Экономия ~1950 строк кода
- ✅ Улучшение архитектуры и тестируемости

---

**ЭТАП 4 ГОТОВ К ЗАПУСКУ!** 🚀

*Приступаю к созданию модульной архитектуры DocumentTool.* 