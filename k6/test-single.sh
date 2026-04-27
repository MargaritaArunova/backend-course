#!/bin/bash

# Скрипт для запуска одиночного теста k6 с заданными параметрами

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Параметры по умолчанию
VUS=${VUS:-10}
DURATION=${DURATION:-"30s"}
BASE_URL=${BASE_URL:-"http://localhost:8080"}
POST_USERS_RATIO=${POST_USERS_RATIO:-"0.5"}

# Вывод информации
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  K6 Single Test Run${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Base URL: ${GREEN}${BASE_URL}${NC}"
echo -e "VUs: ${GREEN}${VUS}${NC}"
echo -e "Duration: ${GREEN}${DURATION}${NC}"
echo -e "POST /users ratio: ${GREEN}${POST_USERS_RATIO}${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Создаем директорию для результатов
mkdir -p k6/results

# Запуск теста
k6 run \
    -e BASE_URL="${BASE_URL}" \
    -e VUS="${VUS}" \
    -e DURATION="${DURATION}" \
    -e POST_USERS_RATIO="${POST_USERS_RATIO}" \
    --vus "${VUS}" \
    --duration "${DURATION}" \
    k6/load-test.js

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Test completed successfully${NC}"
else
    echo -e "\n\033[0;31m✗ Test failed${NC}"
    exit 1
fi
