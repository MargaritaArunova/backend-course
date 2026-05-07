# Конфигурация Kafka Consumer

## Параллелизм и партиции

### Настройка параллелизма

В приложении настроен параллельный consumer через параметр `concurrency` в `@KafkaListener`:

```java
@KafkaListener(
    topics = "${kafka.topic.name}",
    groupId = "${spring.kafka.consumer.group-id}",
    concurrency = "${kafka.listener.concurrency}"  // <-- параллелизм
)
```

### Файл конфигурации (application.properties)

```properties
# Количество партиций в топике
kafka.topic.partitions=3

# Количество параллельных потоков-слушателей
kafka.listener.concurrency=3
```

### Как это работает

1. **Партиции топика**: Топик `entity-operations` создается с 3 партициями
2. **Concurrency**: Spring Kafka создает 3 параллельных потока-слушателя
3. **Распределение**: Каждый поток обрабатывает сообщения из своей партиции

```
Топик: entity-operations
├── Partition 0 → Consumer Thread 1
├── Partition 1 → Consumer Thread 2
└── Partition 2 → Consumer Thread 3
```

### Рекомендации

- **Оптимально**: `concurrency` = `partitions`
- **Допустимо**: `concurrency` < `partitions` (некоторые потоки обработают несколько партиций)
- **Не рекомендуется**: `concurrency` > `partitions` (избыточные потоки будут простаивать)

### Переопределение через переменные окружения

```bash
# В docker-compose.yml или .env
KAFKA_TOPIC_PARTITIONS=5
KAFKA_LISTENER_CONCURRENCY=5
```

```bash
# При запуске приложения
java -jar app.jar \
  -Dkafka.topic.partitions=5 \
  -Dkafka.listener.concurrency=5
```

## Архитектура обработки сообщений

### Поток обработки

```
Kafka Topic → Consumer → EntityOperationsConsumer
                              ↓
                        Routing by entity
                              ↓
            ┌─────────────────┼─────────────────┐
            ↓                 ↓                 ↓
    UserMessageHandler  PostMessageHandler  CommentMessageHandler
            ↓                 ↓                 ↓
      UserService       PostService       CommentService
            ↓                 ↓                 ↓
        Database          Database          Database
```

### Регистрация обработчиков

Обработчики автоматически регистрируются через Spring DI:

```java
@PostConstruct
public void init() {
    messageHandlers.forEach(handler ->
        handlerMap.put(handler.getSupportedEntity().toUpperCase(), handler)
    );
}
```

Каждый обработчик реализует интерфейс `MessageHandler`:

```java
public interface MessageHandler {
    void handle(String operation, String payload);
    String getSupportedEntity();  // "USER", "POST", "COMMENT"
}
```

### Добавление нового обработчика

Чтобы добавить поддержку новой сущности:

1. Создайте класс, реализующий `MessageHandler`
2. Пометьте его аннотацией `@Component`
3. Реализуйте методы `handle()` и `getSupportedEntity()`

Пример:

```java
@Component
@RequiredArgsConstructor
public class LikeMessageHandler implements MessageHandler {

    private final LikeService likeService;

    @Override
    public void handle(String operation, String payload) {
        // Обработка операций
    }

    @Override
    public String getSupportedEntity() {
        return "LIKE";
    }
}
```

Обработчик будет автоматически зарегистрирован при старте приложения.

## Мониторинг

### Проверка количества потоков

Логи при старте:

```
Initialized 3 message handlers: [USER, POST, COMMENT]
```

### Логирование обработки

Каждое сообщение логируется:

```
Received message: {"entity":"USER","operation":"POST","payload":"..."}
Processing USER operation: POST with payload: ...
Successfully processed message for entity: USER with operation: POST
```

## Производительность

### Пропускная способность

С настройками по умолчанию (3 партиции, concurrency=3):
- **Последовательная обработка**: ~100-200 msg/sec на поток
- **Параллельная обработка**: ~300-600 msg/sec всего

### Масштабирование

Для увеличения пропускной способности:

1. Увеличьте количество партиций в топике
2. Увеличьте `concurrency` до соответствующего значения
3. Убедитесь, что база данных выдержит нагрузку

Пример для высоконагруженных систем:

```properties
kafka.topic.partitions=10
kafka.listener.concurrency=10
```

## Отказоустойчивость

- **Автоматические повторы**: Spring Kafka автоматически повторяет при ошибках
- **Логирование ошибок**: Все ошибки логируются с полным stack trace
- **Обработка невалидных сообщений**: Некорректные сообщения пропускаются с логированием

## Тестирование

Используйте Python producer или kafka-console-producer для тестирования:

```bash
# Python
python kafka_producer.py

# Kafka console
./send_test_messages.sh
```