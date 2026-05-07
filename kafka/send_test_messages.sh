#!/bin/bash

# Скрипт для отправки тестовых сообщений в Kafka используя kafka-console-producer.sh

KAFKA_HOST="${KAFKA_HOST:-localhost:9092}"
TOPIC_NAME="${TOPIC_NAME:-entity-operations}"

echo "=========================================="
echo "Отправка тестовых сообщений в Kafka"
echo "Topic: $TOPIC_NAME"
echo "Broker: $KAFKA_HOST"
echo "=========================================="
echo ""

# Проверка доступности kafka-console-producer.sh
if ! command -v kafka-console-producer.sh &> /dev/null; then
    echo "ERROR: kafka-console-producer.sh не найден в PATH"
    echo "Установите Kafka или используйте Python producer: python kafka_producer.py"
    exit 1
fi

# Временный файл с сообщениями
TMP_FILE=$(mktemp)

cat > "$TMP_FILE" << 'EOF'
{"entity":"USER","operation":"POST","payload":"{\"nickname\":\"testuser\",\"email\":\"test@example.com\"}"}
{"entity":"POST","operation":"POST","payload":"{\"authorId\":1,\"text\":\"Hello from Kafka!\"}"}
{"entity":"COMMENT","operation":"POST","payload":"{\"postId\":1,\"authorId\":1,\"text\":\"Great post!\"}"}
EOF

echo "Отправка сообщений..."
cat "$TMP_FILE" | kafka-console-producer.sh --broker-list "$KAFKA_HOST" --topic "$TOPIC_NAME"

rm "$TMP_FILE"

echo ""
echo "✓ Сообщения отправлены!"
echo "=========================================="