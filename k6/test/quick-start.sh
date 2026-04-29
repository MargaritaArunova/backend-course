#!/bin/bash

# Быстрый старт для k6 тестирования
# Этот скрипт выполняет полный цикл: заполнение данными -> тестирование -> построение графиков

set -e

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  K6 Load Testing - Quick Start${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Проверка зависимостей
echo -e "${YELLOW}Проверка зависимостей...${NC}"

# Проверка k6
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}❌ k6 не установлен${NC}"
    echo -e "Установите k6: ${BLUE}brew install k6${NC} (macOS)"
    exit 1
fi
echo -e "${GREEN}✓ k6 установлен${NC}"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не установлен${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 установлен${NC}"

# Проверка доступности сервиса
BASE_URL=${BASE_URL:-"http://localhost:8080"}
echo -e "\n${YELLOW}Проверка доступности сервиса ${BASE_URL}...${NC}"

if curl -s -f "${BASE_URL}/users" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Сервис доступен${NC}"
else
    echo -e "${RED}❌ Сервис недоступен по адресу ${BASE_URL}${NC}"
    echo -e "${YELLOW}Запустите приложение командой: docker-compose up -d${NC}"
    exit 1
fi

# Установка Python зависимостей
echo -e "\n${YELLOW}Установка Python зависимостей...${NC}"
pip3 install -q -r k6/test/requirements.txt
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Шаг 1: Заполнение тестовыми данными
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Шаг 1: Заполнение тестовыми данными${NC}"
echo -e "${BLUE}========================================${NC}"

USER_COUNT=${USER_COUNT:-100}
echo -e "${YELLOW}Создание ${USER_COUNT} пользователей и связанных данных...${NC}"
python3 k6/test/seed-data.py --endpoint users --count ${USER_COUNT}

# Шаг 2: Запуск нагрузочных тестов
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Шаг 2: Запуск нагрузочных тестов${NC}"
echo -e "${BLUE}========================================${NC}"

./k6/test/run-tests.sh

# Шаг 3: Генерация графиков
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Шаг 3: Генерация графиков${NC}"
echo -e "${BLUE}========================================${NC}"

python3 k6/test/plot-results.py

# Готово!
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Все операции завершены успешно!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}Результаты:${NC}"
echo -e "  • Результаты тестов: ${YELLOW}k6/test/results/*.json${NC}"
echo -e "  • Графики: ${YELLOW}k6/test/results/*.png${NC}"
echo -e "\n${BLUE}Для просмотра графиков:${NC}"
echo -e "  ${YELLOW}open k6/test/results/response_time_vs_load.png${NC}"
echo -e "  ${YELLOW}open k6/test/results/combined_metrics.png${NC}\n"
