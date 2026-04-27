# Быстрый старт K6 тестирования

## 1. Установка зависимостей

### K6
```bash
# macOS
brew install k6

# Linux
curl -s https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Python зависимости
```bash
pip3 install -r k6/requirements.txt
```

## 2. Запуск приложения

```bash
# Через Docker
docker-compose up -d

# Или через Gradle
./gradlew bootRun
```

## 3. Автоматический запуск (все в одном)

```bash
./k6/quick-start.sh
```

Этот скрипт выполнит:
1. Проверку зависимостей
2. Заполнение БД тестовыми данными (100 пользователей)
3. Запуск нагрузочных тестов (10, 20, 40, 80, 160 VUs)
4. Генерацию графиков

## 4. Ручной запуск по шагам

### Шаг 1: Заполнить БД данными
```bash
python3 k6/seed-data.py --endpoint users --count 500
```

### Шаг 2: Запустить тесты
```bash
./k6/run-tests.sh
```

### Шаг 3: Построить графики
```bash
python3 k6/plot-results.py
```

## 5. Просмотр результатов

Графики сохраняются в `k6/results/`:
```bash
open k6/results/response_time_vs_load.png
open k6/results/combined_metrics.png
```

## Настройка параметров

### Изменить количество пользователей
```bash
export USER_COUNT=1000
./k6/quick-start.sh
```

### Изменить пропорцию запросов
```bash
# 70% POST /users, 30% GET /statistics/self-likes
export POST_USERS_RATIO="0.7"
./k6/run-tests.sh
```

### Изменить длительность теста
```bash
export DURATION="60s"
./k6/run-tests.sh
```

### Использовать конфигурационный файл
```bash
# Создать конфиг
cp k6/config.example.env k6/config.env

# Отредактировать config.env
nano k6/config.env

# Применить и запустить
source k6/config.env && ./k6/run-tests.sh
```

## Команды для seed-data.py

```bash
# Создать пользователей и связанные данные
python3 k6/seed-data.py --endpoint users --count 500

# Очистить все данные
python3 k6/seed-data.py --endpoint users --clear

# Создать только посты
python3 k6/seed-data.py --endpoint posts --count 200

# Создать комментарии
python3 k6/seed-data.py --endpoint comments --count 100

# Создать лайки
python3 k6/seed-data.py --endpoint likes --count 300
```

## Troubleshooting

### Ошибка: сервис недоступен
```bash
# Проверить статус
curl http://localhost:8080/users

# Проверить Docker
docker-compose ps

# Перезапустить
docker-compose restart
```

### Ошибка: k6 не найден
```bash
# Установить k6
brew install k6
```

### Ошибка: Python модуль не найден
```bash
# Переустановить зависимости
pip3 install -r k6/requirements.txt
```

## Полная документация

Подробная документация доступна в [README.md](README.md)
