#!/bin/bash

# Скрипт для запуска k6 нагрузочных тестов с разными уровнями VUs

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Настройки по умолчанию
BASE_URL=${BASE_URL:-"http://localhost:8080"}
DURATION=${DURATION:-"30s"}
POST_USERS_RATIO=${POST_USERS_RATIO:-"0.5"}

# Массив уровней нагрузки (VUs) - тест удвоения
VUS_LEVELS=(10 20 40 80 160)

# Создаем директорию для результатов
RESULTS_DIR="k6/results"
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  K6 Load Testing - Doubling Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Base URL: ${GREEN}${BASE_URL}${NC}"
echo -e "Duration per test: ${GREEN}${DURATION}${NC}"
echo -e "POST /users ratio: ${GREEN}${POST_USERS_RATIO}${NC}"
echo -e "GET /statistics/self-likes ratio: ${GREEN}$(echo "1 - ${POST_USERS_RATIO}" | bc)${NC}"
echo -e "VUs levels: ${GREEN}${VUS_LEVELS[@]}${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Очищаем старые результаты
rm -f "$RESULTS_DIR"/*.json

# Запускаем тесты для каждого уровня VUs
for VUS in "${VUS_LEVELS[@]}"
do
    echo -e "${YELLOW}Running test with ${VUS} VUs...${NC}"

    k6 run \
        --out json="$RESULTS_DIR/raw_${VUS}vus.json" \
        -e BASE_URL="$BASE_URL" \
        -e VUS="$VUS" \
        -e DURATION="$DURATION" \
        -e POST_USERS_RATIO="$POST_USERS_RATIO" \
        --vus "$VUS" \
        --duration "$DURATION" \
        k6/load-test.js

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test with ${VUS} VUs completed successfully${NC}\n"
    else
        echo -e "\033[0;31m✗ Test with ${VUS} VUs failed${NC}\n"
    fi

    # Пауза между тестами
    sleep 5
done

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Results saved in: ${GREEN}${RESULTS_DIR}/${NC}"
echo -e "\nTo generate charts, run:"
echo -e "${YELLOW}python3 k6/plot-results.py${NC}\n"
