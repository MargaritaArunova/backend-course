# K6 Load Testing Configuration

Конфигурация для нагрузочного тестирования REST API с использованием k6.

## Структура

```
k6/
├── load-test.js          # Основной скрипт k6 для нагрузочного тестирования
├── run-tests.sh          # Bash скрипт для запуска тестов с разными уровнями нагрузки
├── plot-results.py       # Python скрипт для генерации графиков
├── seed-data.py          # Python скрипт для заполнения БД тестовыми данными
├── requirements.txt      # Python зависимости
└── results/              # Директория для результатов тестов (создается автоматически)
```

## Требования

### K6
```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Python
```bash
# Установка зависимостей
pip install -r k6/requirements.txt
```

## Быстрый старт

### 1. Запуск приложения

Убедитесь, что ваше приложение запущено:

```bash
# Запуск через Docker Compose
docker-compose up -d

# Или через Gradle
./gradlew bootRun
```

### 2. Заполнение тестовыми данными

```bash
# Создать 500 пользователей и связанные данные (посты, комментарии, лайки)
python3 k6/seed-data.py --endpoint users --count 500

# Создать 100 пользователей
python3 k6/seed-data.py --endpoint users --count 100

# Очистить все данные
python3 k6/seed-data.py --endpoint users --clear
```

### 3. Запуск нагрузочных тестов

```bash
# Сделать скрипт исполняемым
chmod +x k6/run-tests.sh

# Запустить тесты
./k6/run-tests.sh
```

Тесты будут запущены с уровнями нагрузки: 10, 20, 40, 80, 160 VUs (Virtual Users).

### 4. Генерация графиков

```bash
python3 k6/plot-results.py
```

Графики будут сохранены в `k6/results/`:
- `response_time_vs_load.png` - зависимость времени отклика от нагрузки
- `combined_metrics.png` - комбинированный график всех метрик

## Конфигурация

### Переменные окружения для load-test.js

- `BASE_URL` - базовый URL API (по умолчанию: `http://localhost:8080`)
- `POST_USERS_RATIO` - доля запросов POST /users (по умолчанию: `0.5` = 50%)
- `VUS` - количество виртуальных пользователей
- `DURATION` - длительность теста (по умолчанию: `30s`)

### Настройка run-tests.sh

Отредактируйте массив `VUS_LEVELS` в файле для изменения уровней нагрузки:

```bash
VUS_LEVELS=(10 20 40 80 160)  # Тест удвоения
```

Или используйте переменные окружения:

```bash
# Изменить базовый URL
export BASE_URL="http://localhost:9090"

# Изменить длительность теста
export DURATION="60s"

# Изменить пропорцию запросов
export POST_USERS_RATIO="0.7"  # 70% POST /users, 30% GET /statistics/self-likes

./k6/run-tests.sh
```

## Примеры использования

### Запуск одного теста

```bash
k6 run \
  -e BASE_URL="http://localhost:8080" \
  -e VUS="50" \
  -e DURATION="60s" \
  -e POST_USERS_RATIO="0.5" \
  --vus 50 \
  --duration 60s \
  k6/load-test.js
```

### Заполнение данными

```bash
# Создать пользователей и связанные данные
python3 k6/seed-data.py --endpoint users --count 1000

# Создать только посты (требуются существующие пользователи)
python3 k6/seed-data.py --endpoint posts --count 500

# Создать комментарии
python3 k6/seed-data.py --endpoint comments --count 300

# Создать лайки
python3 k6/seed-data.py --endpoint likes --count 1000

# Очистить только посты
python3 k6/seed-data.py --endpoint posts --clear

# Использовать другой URL
python3 k6/seed-data.py --endpoint users --count 100 --base-url http://localhost:9090
```

## Тестируемые endpoints

1. **POST /users** - создание пользователя
   - Body: `{ "nickname": "string", "email": "string" }`
   - Response: `{ "id": number, "nickname": "string", "email": "string", "registeredAt": "string" }`

2. **GET /statistics/self-likes** - получение статистики пользователей, лайкнувших свои посты
   - Response: массив объектов статистики

## Метрики

k6 собирает следующие метрики:

- `http_req_duration` - время выполнения запроса
  - `avg` - среднее время
  - `p(95)` - 95-й перцентиль
  - `min` - минимальное время
  - `max` - максимальное время
- `http_req_failed` - процент неудачных запросов
- `http_reqs` - общее количество запросов
- `post_users_requests` - счетчик POST /users запросов
- `get_stats_requests` - счетчик GET /statistics/self-likes запросов

## Интерпретация результатов

### Хорошие показатели:
- Avg response time < 200ms
- P95 response time < 500ms
- Failed requests < 1%
- Линейная зависимость времени от нагрузки (без резких скачков)

### Проблемы:
- Резкое увеличение времени отклика при росте VUs - узкое место в приложении
- Высокий процент ошибок - недостаточная производительность или проблемы с БД
- Большая разница между avg и p95 - нестабильная производительность

## Troubleshooting

### Ошибка подключения к БД

Убедитесь, что PostgreSQL запущен:

```bash
docker-compose ps
```

### k6 не установлен

Установите k6 согласно инструкции выше.

### Python зависимости не установлены

```bash
pip install -r k6/requirements.txt
```

### Приложение не отвечает

Проверьте, что приложение запущено:

```bash
curl http://localhost:8080/users
```

## Расширенные возможности

### Изменение пропорции запросов

Создайте файл конфигурации:

```bash
# config.env
export BASE_URL="http://localhost:8080"
export DURATION="45s"
export POST_USERS_RATIO="0.3"  # 30% POST, 70% GET

source config.env
./k6/run-tests.sh
```

### Профилирование конкретного endpoint

Отредактируйте `load-test.js`, установив `POST_USERS_RATIO` в `1.0` для тестирования только POST /users или `0.0` для GET /statistics/self-likes.

### Интеграция с CI/CD

```yaml
# .github/workflows/load-test.yml
name: Load Tests
on: [push]
jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install k6
        run: |
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      - name: Run tests
        run: ./k6/run-tests.sh
```
