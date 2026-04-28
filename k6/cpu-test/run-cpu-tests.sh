#!/bin/bash

# Скрипт для тестирования зависимости времени отклика от количества CPU
# при разных соотношениях операций вставка/чтение

set -e

# Настройки теста
VUS=50                    # Постоянное количество виртуальных пользователей
DURATION="3m"             # Длительность каждого теста
BASE_URL="http://localhost:8080"

# Соотношения вставка/чтение для тестирования
WRITE_RATIOS=("0.05" "0.50" "0.95")  # 5/95, 50/50, 95/5
WRITE_RATIO_LABELS=("5_95" "50_50" "95_5")

# Настройки CPU (в ядрах)
# Определим минимум, максимум и шаг
CPU_MIN=0.5
CPU_MAX=4.0
CPU_STEP=0.5

# Директория для результатов
RESULTS_DIR="./results"
mkdir -p "$RESULTS_DIR"

# Файл для сводных результатов
SUMMARY_FILE="$RESULTS_DIR/summary.csv"

# Путь к docker-compose файлу
DOCKER_COMPOSE_FILE="../../docker-compose.yml"

# Функция для получения текущего количества CPU
get_current_cpu() {
    docker inspect hl-module1-app --format='{{.HostConfig.NanoCpus}}' 2>/dev/null | awk '{print $1/1000000000}' || echo "0"
}

# Функция для установки CPU лимита
set_cpu_limit() {
    local cpu_limit=$1
    echo "Setting CPU limit to ${cpu_limit} cores..."

    export APP_CPU_LIMIT="${cpu_limit}"
    export APP_CPU_RESERVATION="${cpu_limit}"

    # Пересоздаем контейнер с новыми лимитами
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --force-recreate app

    # Ждем, пока приложение запустится
    echo "Waiting for application to start..."
    sleep 20

    # Проверяем доступность
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/users" | grep -q "200"; then
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
    python3 ../seed-data.py --clear-all --base-url "$BASE_URL" || echo "Warning: Failed to clear database"
    sleep 2
}

# Функция для запуска теста
run_test() {
    local cpu_limit=$1
    local write_ratio=$2
    local ratio_label=$3

    local test_name="cpu_${cpu_limit}_ratio_${ratio_label}"
    local output_file="$RESULTS_DIR/${test_name}.json"

    echo ""
    echo "=========================================="
    echo "Running test: $test_name"
    echo "CPU: ${cpu_limit} cores"
    echo "Write ratio: ${write_ratio} (${ratio_label})"
    echo "VUs: $VUS"
    echo "Duration: $DURATION"
    echo "=========================================="

    # Очищаем базу перед тестом
    clear_database

    # Запускаем k6 тест
    k6 run \
        --out json="$output_file" \
        -e BASE_URL="$BASE_URL" \
        -e WRITE_RATIO="$write_ratio" \
        -e VUS="$VUS" \
        -e DURATION="$DURATION" \
        load-test.js

    echo "Test completed: $test_name"
    echo "Results saved to: $output_file"
}

# Функция для извлечения метрик из JSON
extract_metrics() {
    local json_file=$1

    # Используем jq для извлечения метрик (если установлен)
    if command -v jq &> /dev/null; then
        local read_p95=$(jq -r '.metrics.read_response_time.values.p95 // "N/A"' "$json_file")
        local write_p95=$(jq -r '.metrics.write_response_time.values.p95 // "N/A"' "$json_file")
        local http_req_duration_p95=$(jq -r '.metrics.http_req_duration.values.p95 // "N/A"' "$json_file")

        echo "$read_p95,$write_p95,$http_req_duration_p95"
    else
        echo "N/A,N/A,N/A"
    fi
}

# Основная функция
main() {
    echo "CPU Performance Test Suite"
    echo "=========================="
    echo "VUs: $VUS"
    echo "Test duration: $DURATION"
    echo "CPU range: ${CPU_MIN} - ${CPU_MAX} (step ${CPU_STEP})"
    echo "Write ratios: ${WRITE_RATIO_LABELS[*]}"
    echo ""

    # Создаем заголовок для CSV
    echo "CPU,WriteRatio,RatioLabel,ReadP95,WriteP95,OverallP95" > "$SUMMARY_FILE"

    # Перебираем значения CPU
    cpu=$CPU_MIN
    while (( $(echo "$cpu <= $CPU_MAX" | bc -l) )); do
        echo ""
        echo "=========================================="
        echo "Testing with CPU: ${cpu} cores"
        echo "=========================================="

        # Устанавливаем CPU лимит
        set_cpu_limit "$cpu"

        # Перебираем соотношения вставка/чтение
        for i in "${!WRITE_RATIOS[@]}"; do
            write_ratio="${WRITE_RATIOS[$i]}"
            ratio_label="${WRITE_RATIO_LABELS[$i]}"

            # Запускаем тест
            run_test "$cpu" "$write_ratio" "$ratio_label"

            # Извлекаем метрики и добавляем в сводный файл
            output_file="$RESULTS_DIR/cpu_${cpu}_ratio_${ratio_label}.json"
            metrics=$(extract_metrics "$output_file")
            echo "${cpu},${write_ratio},${ratio_label},${metrics}" >> "$SUMMARY_FILE"

            # Пауза между тестами
            sleep 5
        done

        # Увеличиваем CPU
        cpu=$(echo "$cpu + $CPU_STEP" | bc)
    done

    echo ""
    echo "=========================================="
    echo "All tests completed!"
    echo "Summary saved to: $SUMMARY_FILE"
    echo "=========================================="

    # Выводим сводную таблицу
    if [ -f "$SUMMARY_FILE" ]; then
        echo ""
        echo "Summary:"
        cat "$SUMMARY_FILE"
    fi
}

# Запускаем основную функцию
main