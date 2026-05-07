# Kafka Producer для тестирования

Этот каталог содержит инструменты для отправки тестовых сообщений в Kafka.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Использование Python Producer

### Автоматический режим (тестовые сообщения)

```bash
python kafka_producer.py
```

Этот режим отправляет предопределенный набор тестовых сообщений для всех типов операций.

### Интерактивный режим

```bash
python kafka_producer.py --interactive
```

В интерактивном режиме вы можете вручную вводить сообщения.

Пример:
```
Entity (USER/POST/COMMENT): USER
Operation (POST/PUT/DEL): POST
Payload (JSON):
{"nickname": "john_doe", "email": "john@example.com"}
```

## Использование kafka-console-producer.sh

Если у вас установлен Kafka локально, вы можете использовать стандартный kafka-console-producer:

```bash
# Подключение к топику
kafka-console-producer.sh --broker-list localhost:9092 --topic entity-operations
```

Затем введите JSON-сообщения:

```json
{"entity":"USER","operation":"POST","payload":"{\"nickname\":\"testuser\",\"email\":\"test@example.com\"}"}
{"entity":"POST","operation":"POST","payload":"{\"authorId\":1,\"text\":\"Hello World!\"}"}
{"entity":"COMMENT","operation":"POST","payload":"{\"postId\":1,\"authorId\":1,\"text\":\"Great post!\"}"}
{"entity":"USER","operation":"DEL","payload":"1"}
```

## Формат сообщений

Все сообщения должны соответствовать следующему формату:

```json
{
  "entity": "USER|POST|COMMENT",
  "operation": "POST|PUT|DEL|DELETE",
  "payload": "<JSON-строка или ID>"
}
```

### Примеры для разных операций

#### USER

**Создание (POST):**
```json
{
  "entity": "USER",
  "operation": "POST",
  "payload": "{\"nickname\":\"john_doe\",\"email\":\"john@example.com\"}"
}
```

**Обновление (PUT):**
```json
{
  "entity": "USER",
  "operation": "PUT",
  "payload": "{\"id\":1,\"nickname\":\"john_updated\",\"email\":\"john_new@example.com\"}"
}
```

**Удаление (DEL):**
```json
{
  "entity": "USER",
  "operation": "DEL",
  "payload": "1"
}
```

#### POST

**Создание (POST):**
```json
{
  "entity": "POST",
  "operation": "POST",
  "payload": "{\"authorId\":1,\"text\":\"My awesome post!\"}"
}
```

**Удаление (DEL):**
```json
{
  "entity": "POST",
  "operation": "DEL",
  "payload": "1"
}
```

#### COMMENT

**Создание (POST):**
```json
{
  "entity": "COMMENT",
  "operation": "POST",
  "payload": "{\"postId\":1,\"authorId\":1,\"text\":\"Nice!\"}"
}
```

**Удаление (DEL):**
```json
{
  "entity": "COMMENT",
  "operation": "DEL",
  "payload": "{\"postId\":1,\"id\":1}"
}
```

## Настройка параллелизма

В `application.properties` настроены следующие параметры:

- `kafka.topic.partitions=3` - количество партиций в топике
- `kafka.listener.concurrency=3` - количество потоков-слушателей

Эти параметры можно переопределить через переменные окружения:
- `KAFKA_TOPIC_PARTITIONS`
- `KAFKA_LISTENER_CONCURRENCY`

Рекомендуется, чтобы количество партиций было равно или больше количества потоков-слушателей для оптимальной производительности.