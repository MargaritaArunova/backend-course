#!/bin/bash

# Скрипт для быстрого просмотра observability статистики из логов

set -e

LOGS_DIR="./results/logs"

if [ ! -d "$LOGS_DIR" ]; then
    echo "Директория с логами не найдена: $LOGS_DIR"
    echo "Запустите сначала ./run-cpu-tests.sh"
    exit 1
fi

echo "=========================================="
echo "OBSERVABILITY СТАТИСТИКА"
echo "=========================================="
echo ""

# Показываем статистику для каждого CPU лимита
for stats_file in "$LOGS_DIR"/cpu_*_stats.txt; do
    if [ ! -f "$stats_file" ]; then
        continue
    fi

    # Извлекаем CPU из имени файла
    cpu=$(basename "$stats_file" | sed 's/cpu_//; s/_stats.txt//')

    echo ""
    echo "==========================================">
    echo "CPU: $cpu cores"
    echo "=========================================="
    echo ""

    # Показываем содержимое файла статистики
    cat "$stats_file"

    echo ""
    echo "------------------------------------------"
    echo ""
done

echo ""
echo "=========================================="
echo "Для построения графиков запустите:"
echo "  ./analyze-results.py"
echo "=========================================="