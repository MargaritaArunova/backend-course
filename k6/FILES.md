# Структура файлов K6 тестирования

## Основные файлы

### 📋 load-test.js
**Основной скрипт k6 для нагрузочного тестирования**

- Тестирует endpoints: POST /users и GET /statistics/self-likes
- Настраиваемая пропорция запросов (по умолчанию 50/50)
- Собирает метрики: avg, p95, min, max response time
- Сохраняет результаты в JSON формате

**Переменные окружения:**
- `BASE_URL` - базовый URL API (по умолчанию: http://localhost:8080)
- `POST_USERS_RATIO` - доля POST запросов (по умолчанию: 0.5)
- `VUS` - количество виртуальных пользователей
- `DURATION` - длительность теста (по умолчанию: 30s)

### 🚀 run-tests.sh
**Bash скрипт для запуска тестов с разными уровнями нагрузки**

- Запускает тесты с уровнями VUs: 10, 20, 40, 80, 160 (тест удвоения)
- Создает директорию results/
- Сохраняет результаты для каждого уровня нагрузки
- Выводит красивый цветной прогресс

**Использование:**
```bash
./k6/run-tests.sh
```

### 📊 plot-results.py
**Python скрипт для генерации графиков**

- Строит график зависимости avg response time от VUs
- Строит график зависимости p95 response time от VUs
- Создает комбинированный график всех метрик
- Выводит таблицу с результатами

**Использование:**
```bash
python3 k6/plot-results.py
```

**Генерируемые графики:**
- `k6/results/response_time_vs_load.png` - основной график
- `k6/results/combined_metrics.png` - комбинированный график

### 🌱 seed-data.py
**Python скрипт для заполнения БД тестовыми данными**

- Поддерживает endpoints: users, posts, comments, likes
- Генерирует реалистичные данные с помощью Faker
- Учитывает зависимости между таблицами
- Может очищать данные перед заполнением

**Параметры:**
- `--endpoint` - эндпоинт (users, posts, comments, likes)
- `--count` - количество объектов (по умолчанию: 500)
- `--clear` - очистить данные
- `--base-url` - URL API (по умолчанию: http://localhost:8080)

**Примеры:**
```bash
# Создать 500 пользователей и связанные данные
python3 k6/seed-data.py --endpoint users --count 500

# Очистить все данные
python3 k6/seed-data.py --endpoint users --clear

# Создать 200 постов
python3 k6/seed-data.py --endpoint posts --count 200
```

## Вспомогательные скрипты

### ⚡ quick-start.sh
**Автоматический запуск полного цикла тестирования**

Выполняет:
1. Проверку зависимостей (k6, Python, библиотеки)
2. Проверку доступности сервиса
3. Заполнение БД тестовыми данными
4. Запуск нагрузочных тестов
5. Генерацию графиков

**Использование:**
```bash
./k6/quick-start.sh
```

**Переменные окружения:**
- `USER_COUNT` - количество пользователей для создания (по умолчанию: 100)
- `BASE_URL` - URL API
- `DURATION` - длительность теста
- `POST_USERS_RATIO` - пропорция запросов

### 🧪 test-single.sh
**Запуск одиночного теста с заданными параметрами**

**Использование:**
```bash
# С параметрами по умолчанию (10 VUs, 30s)
./k6/test-single.sh

# С кастомными параметрами
VUS=50 DURATION=60s ./k6/test-single.sh

# Изменить пропорцию
POST_USERS_RATIO=0.7 ./k6/test-single.sh
```

### ✅ check-env.sh
**Проверка окружения перед запуском тестов**

Проверяет:
- Установлен ли k6
- Установлен ли Python 3 и pip3
- Установлены ли Python зависимости
- Доступен ли REST API сервис
- Присутствуют ли все необходимые файлы

**Использование:**
```bash
./k6/check-env.sh
```

## Конфигурационные файлы

### 📦 requirements.txt
**Python зависимости**

Содержит:
- `requests` - для HTTP запросов
- `Faker` - для генерации тестовых данных
- `matplotlib` - для построения графиков
- `numpy` - для математических операций

**Установка:**
```bash
pip3 install -r k6/requirements.txt
```

### 🔧 config.example.env
**Пример конфигурационного файла**

Содержит примеры настроек для различных сценариев тестирования.

**Использование:**
```bash
cp k6/config.example.env k6/config.env
nano k6/config.env
source k6/config.env && ./k6/run-tests.sh
```

### 🚫 .gitignore
**Исключения для Git**

Игнорирует:
- Директорию results/
- JSON файлы результатов
- Python кеш
- IDE конфигурации

## Документация

### 📖 README.md
**Полная документация**

Содержит:
- Подробные инструкции по установке
- Описание всех компонентов
- Примеры использования
- Интерпретация результатов
- Troubleshooting
- Расширенные возможности

### 🚀 QUICKSTART.md
**Быстрый старт**

Содержит:
- Краткие инструкции по установке
- Команды для быстрого запуска
- Основные команды
- Troubleshooting

### 📄 FILES.md (этот файл)
**Описание всех файлов**

## Директории

### 📁 results/
**Директория для результатов тестирования** (создается автоматически)

Содержит:
- `result_*vus.json` - результаты для каждого уровня VUs
- `raw_*vus.json` - полные данные k6
- `*.png` - графики результатов

**Примечание:** Эта директория игнорируется Git'ом.

## Рекомендуемый порядок использования

### Первый запуск

1. Проверить окружение:
   ```bash
   ./k6/check-env.sh
   ```

2. Если все OK, запустить автоматический тест:
   ```bash
   ./k6/quick-start.sh
   ```

3. Посмотреть результаты:
   ```bash
   open k6/results/response_time_vs_load.png
   ```

### Кастомное тестирование

1. Создать конфигурацию:
   ```bash
   cp k6/config.example.env k6/config.env
   nano k6/config.env
   ```

2. Заполнить БД:
   ```bash
   python3 k6/seed-data.py --endpoint users --count 1000
   ```

3. Запустить тесты:
   ```bash
   source k6/config.env && ./k6/run-tests.sh
   ```

4. Построить графики:
   ```bash
   python3 k6/plot-results.py
   ```

### Разработка и отладка

1. Запустить одиночный тест:
   ```bash
   VUS=10 DURATION=10s ./k6/test-single.sh
   ```

2. Проверить данные:
   ```bash
   curl http://localhost:8080/users | jq
   ```

3. Очистить БД:
   ```bash
   python3 k6/seed-data.py --endpoint users --clear
   ```

## Полезные команды

### Просмотр результатов
```bash
# Список файлов результатов
ls -lh k6/results/

# Просмотр результата
cat k6/results/result_10vus.json | jq

# Открыть график
open k6/results/response_time_vs_load.png
```

### Очистка
```bash
# Удалить все результаты
rm -rf k6/results/

# Очистить БД
python3 k6/seed-data.py --endpoint users --clear
```

### Тестирование
```bash
# Быстрый тест
VUS=5 DURATION=10s ./k6/test-single.sh

# Только POST /users
POST_USERS_RATIO=1.0 ./k6/test-single.sh

# Только GET /statistics/self-likes
POST_USERS_RATIO=0.0 ./k6/test-single.sh
```
