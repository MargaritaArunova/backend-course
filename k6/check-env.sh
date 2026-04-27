#!/bin/bash

# Скрипт для проверки окружения перед запуском тестов

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Environment Check for K6 Testing${NC}"
echo -e "${BLUE}========================================${NC}\n"

ALL_OK=true

# Проверка k6
echo -n "Checking k6... "
if command -v k6 &> /dev/null; then
    K6_VERSION=$(k6 version | head -1)
    echo -e "${GREEN}✓ ${K6_VERSION}${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "  Install: ${YELLOW}brew install k6${NC} (macOS)"
    ALL_OK=false
fi

# Проверка Python 3
echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    ALL_OK=false
fi

# Проверка pip3
echo -n "Checking pip3... "
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ pip ${PIP_VERSION}${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    ALL_OK=false
fi

# Проверка Python зависимостей
echo -e "\n${YELLOW}Python dependencies:${NC}"

REQUIRED_PACKAGES=("requests" "faker" "matplotlib" "numpy")
for package in "${REQUIRED_PACKAGES[@]}"; do
    echo -n "  $package... "
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print($package.__version__ if hasattr($package, '__version__') else 'installed')" 2>/dev/null)
        echo -e "${GREEN}✓ ${VERSION}${NC}"
    else
        echo -e "${RED}✗ Not installed${NC}"
        echo -e "    Install: ${YELLOW}pip3 install -r k6/requirements.txt${NC}"
        ALL_OK=false
    fi
done

# Проверка доступности сервиса
echo -e "\n${YELLOW}Service availability:${NC}"
BASE_URL=${BASE_URL:-"http://localhost:8080"}
echo -n "  Checking ${BASE_URL}... "

if curl -s -f "${BASE_URL}/users" -o /dev/null 2>&1; then
    echo -e "${GREEN}✓ Available${NC}"
else
    echo -e "${RED}✗ Not available${NC}"
    echo -e "    Start service: ${YELLOW}docker-compose up -d${NC}"
    ALL_OK=false
fi

# Проверка структуры директорий
echo -e "\n${YELLOW}Directory structure:${NC}"
REQUIRED_FILES=(
    "k6/load-test.js"
    "k6/run-tests.sh"
    "k6/plot-results.py"
    "k6/seed-data.py"
    "k6/requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    echo -n "  $file... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ Missing${NC}"
        ALL_OK=false
    fi
done

# Итог
echo -e "\n${BLUE}========================================${NC}"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo -e "Ready to run tests:"
    echo -e "  ${YELLOW}./k6/quick-start.sh${NC}      - Full automated run"
    echo -e "  ${YELLOW}./k6/run-tests.sh${NC}        - Run load tests only"
    echo -e "  ${YELLOW}./k6/test-single.sh${NC}      - Run single test"
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo -e "Fix the issues above before running tests."
fi
echo ""
