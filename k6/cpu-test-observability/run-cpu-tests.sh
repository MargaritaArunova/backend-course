#!/bin/bash

# Скрипт для тестирования observability с разными CPU лимитами
# Собирает статистику из логов приложения

set -e

REMOTE_HOST="marunova-backend"
REMOTE_COMPOSE_DIR="~/backend-course"
BASE_URL="http://192.168.1.100:8080"
BASE_ADDITIONAL_URL="http://192.168.1.100:8081"
REMOTE="ssh ${REMOTE_HOST}"
CONTAINER_NAME="backend-course-app"

# Настройки теста
VUS=50                    # Постоянное количество виртуальных пользователей
DURATION=2m              # Длительность каждого теста (увеличено для сбора статистики)

# Настройки CPU для тестирования
CPU_LIMITS=("0.5" "1.0")

# Директория для результатов
RESULTS_DIR="./results"
LOGS_DIR="$RESULTS_DIR/logs"
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# Путь к docker-compose файлу
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Функция для установки CPU лимита
set_cpu_limit() {
    local cpu_limit=$1
    echo "Setting CPU limit to ${cpu_limit} cores..."

    export APP_CPU_LIMIT="${cpu_limit}"
    export APP_CPU_RESERVATION="${cpu_limit}"

    # Пересоздаем контейнер с новыми лимитами (это также очистит логи)
    $REMOTE "cd $REMOTE_COMPOSE_DIR && docker compose -f $DOCKER_COMPOSE_FILE up -d --force-recreate"

    # Ждем, пока приложение запустится
    echo "Waiting for application to start..."
    sleep 30

    # Проверяем доступность
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$BASE_ADDITIONAL_URL/statistics/self-likes" | grep -q "200"; then
            echo "Application is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Application not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "ERROR: Application failed to start"
    return 1
}

# Функция для очистки базы данных
clear_database() {
    echo "Clearing database..."
    $REMOTE "python3 $REMOTE_COMPOSE_DIR/k6/test/seed-data.py --clear-all || echo 'Warning: Failed to clear database'"
    sleep 2
}

# Функция для начала сбора логов
start_log_collection() {
    local test_name=$1
    local log_file="$LOGS_DIR/${test_name}.log"

    echo "Starting log collection for $test_name..."

    # Запускаем сбор логов в фоне на удаленной машине и сохраняем их локально
    $REMOTE "docker logs backend-course-app -f --tail 100" > "$log_file" 2>&1 &
    LOG_PID=$!

    echo "Log collection started with PID: $LOG_PID"
    echo "Logs will be saved to: $log_file"

    # Даем время на начало сбора
    sleep 2
}

# Функция для очистки логов контейнера
clear_container_logs() {
    echo "Clearing container logs..."
    # Перезапускаем контейнер для очистки логов
    $REMOTE "docker restart $CONTAINER_NAME"

    # Ждем пока приложение снова запустится
    echo "Waiting for application to restart..."
    sleep 20

    # Проверяем доступность
    local max_attempts=20
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/users" | grep -q "200"; then
            echo "Application is ready after restart!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Waiting for application..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "WARNING: Application might not be fully ready"
}

# Функция для извлечения observability статистики из логов контейнера
extract_observability_stats() {
    local test_name=$1
    local log_file="$LOGS_DIR/${test_name}.log"
    local stats_file="$LOGS_DIR/${test_name}_stats.txt"

    echo "Fetching logs from container..."

    # Получаем все логи из контейнера
    $REMOTE "docker logs $CONTAINER_NAME" > "$log_file" 2>&1

    echo "Logs saved to: $log_file"
    echo "Extracting observability statistics..."

    # Извлекаем все блоки со статистикой observability
    # Используем awk для извлечения блоков между маркерами
    awk '/=== Observability Statistics ===/{flag=1} flag; /================================/{if(flag) flag=0}' "$log_file" > "$stats_file"

    # Проверяем, нашли ли мы статистику
    if [ -s "$stats_file" ]; then
        local stats_count=$(grep -c "=== Observability Statistics ===" "$stats_file" || echo "0")
        echo "Found $stats_count observability statistics blocks"
        echo "Statistics saved to: $stats_file"
    else
        echo "No observability statistics found in logs" > "$stats_file"
        echo "WARNING: No observability statistics found!"
    fi
}

# Функция для запуска теста
run_test() {
    local cpu_limit=$1
    local test_name="cpu_${cpu_limit}"
    local output_file="$RESULTS_DIR/${test_name}.json"

    echo ""
    echo "=========================================="
    echo "Running test: $test_name"
    echo "CPU: ${cpu_limit} cores"
    echo "VUs: $VUS"
    echo "Duration: $DURATION"
    echo "=========================================="

    # Очищаем логи контейнера перед тестом
#    clear_container_logs

    echo "Starting K6 test..."

    # Запускаем k6 тест
    k6 run \
        --out json="$output_file" \
        -e BASE_URL="$BASE_URL" \
        -e BASE_ADDITIONAL_URL="$BASE_ADDITIONAL_URL" \
        -e VUS="$VUS" \
        -e DURATION="$DURATION" \
        load-test.js

    # Даем время на завершение записи последней статистики
    echo "Waiting for final statistics to be logged..."
    sleep 20

    # Извлекаем observability статистику из логов контейнера
    extract_observability_stats "$test_name"

    echo ""
    echo "Test completed: $test_name"
    echo "Results saved to: $output_file"
    echo "Logs saved to: $LOGS_DIR/${test_name}.log"
    echo "Stats saved to: $LOGS_DIR/${test_name}_stats.txt"
    echo ""
}

# Основная функция
main() {
    echo "Observability CPU Performance Test Suite"
    echo "========================================="
    echo "VUs: $VUS"
    echo "Test duration: $DURATION"
    echo "CPU limits: ${CPU_LIMITS[*]}"
    echo ""

    # Перебираем значения CPU
    for cpu in "${CPU_LIMITS[@]}"; do
        echo ""
        echo "=========================================="
        echo "Testing with CPU: ${cpu} cores"
        echo "=========================================="

        # Устанавливаем CPU лимит
        set_cpu_limit "$cpu"

        # Очищаем базу данных перед тестом
        # clear_database

        # Запускаем тест
        run_test "$cpu"

        # Пауза между тестами
        echo "Waiting before next test..."
        sleep 10
    done

    echo ""
    echo "=========================================="
    echo "All tests completed!"
    echo "=========================================="
    echo ""
    echo "Results saved in: $RESULTS_DIR"
    echo "Logs saved in: $LOGS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Run './analyze-results.py' to generate graphs"
    echo "  2. Check logs in $LOGS_DIR for detailed observability statistics"
}

export APP_ADDITIONAL_CPU_LIMIT=0.5
export APP_ADDITIONAL_MEMORY_LIMIT=512M
export APP_ADDITIONAL_CPU_RESERVATION=0.2
export APP_ADDITIONAL_MEMORY_RESERVATION=256M
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=hl_postgres
export DB_HOST=hl12.zil
export DB_PORT=5433
export DB_NAME=hl10
export TOMCAT_MAX_THREADS=200
export BACKEND_APP_URL="http://app:8080"

# Обработка прерывания
trap 'echo "Interrupted! Exiting..."; exit 1' INT TERM

# Запускаем основную функцию
main

