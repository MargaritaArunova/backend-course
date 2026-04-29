#!/bin/bash

# Скрипт для быстрого локального тестирования (без изменения CPU лимитов)
# Полезен для проверки работоспособности тестов

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
VUS="${VUS:-20}"
DURATION="${DURATION:-30s}"

# Директория для результатов
RESULTS_DIR="./results"
mkdir -p "$RESULTS_DIR"

OUTPUT_FILE="$RESULTS_DIR/local_test.json"

echo "=========================================="
echo "Local Observability Test"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "VUs: $VUS"
echo "Duration: $DURATION"
echo "Output: $OUTPUT_FILE"
echo "=========================================="
echo ""

# Проверяем доступность сервера
echo "Checking server availability..."
if ! curl -s -f "$BASE_URL/users" > /dev/null; then
    echo "ERROR: Server is not available at $BASE_URL"
    echo "Make sure the application is running"
    exit 1
fi

echo "Server is available!"
echo ""

# Запускаем тест
echo "Starting K6 test..."
k6 run \
    --out json="$OUTPUT_FILE" \
    -e BASE_URL="$BASE_URL" \
    -e VUS="$VUS" \
    -e DURATION="$DURATION" \
    load-test.js

echo ""
echo "=========================================="
echo "Test completed!"
echo "Results saved to: $OUTPUT_FILE"
echo "=========================================="
echo ""
echo "Quick summary:"

# Показываем быструю статистику (если установлен jq)
if command -v jq &> /dev/null; then
    echo ""
    echo "Processing results..."

    # Подсчитываем метрики
    jq -r 'select(.type=="Point") | select(.metric=="http_req_duration") | .data.value' "$OUTPUT_FILE" | \
    awk '{sum+=$1; count++; if(min==""){min=max=$1}; if($1>max){max=$1}; if($1<min){min=$1}} END {
        if(count>0) {
            avg=sum/count;
            print "HTTP Request Duration:"
            print "  Count: " count
            print "  Mean:  " avg " ms"
            print "  Min:   " min " ms"
            print "  Max:   " max " ms"
        }
    }'
else
    echo "Install 'jq' for detailed statistics: brew install jq"
    echo "Or run: ./analyze-results.py"
fi

echo ""
echo "For detailed analysis run:"
echo "  ./analyze-results.py"