#!/usr/bin/env python3
"""
Kafka Producer для отправки тестовых сообщений в топик entity-operations.
Использование: python kafka_producer.py
"""

import json
import sys
from kafka import KafkaProducer
from kafka.errors import KafkaError


def create_producer(bootstrap_servers='localhost:9092'):
    """Создает и возвращает Kafka producer."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        print(f"✓ Подключено к Kafka на {bootstrap_servers}")
        return producer
    except KafkaError as e:
        print(f"✗ Ошибка подключения к Kafka: {e}")
        sys.exit(1)


def send_message(producer, topic, entity, operation, payload):
    """Отправляет сообщение в Kafka."""
    message = {
        "entity": entity,
        "operation": operation,
        "payload": json.dumps(payload) if isinstance(payload, dict) else str(payload)
    }

    try:
        future = producer.send(topic, value=message)
        record_metadata = future.get(timeout=10)
        print(f"✓ Сообщение отправлено в топик '{record_metadata.topic}' "
              f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})")
        print(f"  Entity: {entity}, Operation: {operation}")
        return True
    except KafkaError as e:
        print(f"✗ Ошибка отправки сообщения: {e}")
        return False


def main():
    """Главная функция с примерами отправки сообщений."""
    topic_name = 'entity-operations'
    producer = create_producer()

    print("\n" + "="*60)
    print("Kafka Producer - Отправка тестовых сообщений")
    print("="*60 + "\n")

    # Пример 1: Создание пользователя
    print("1. Создание пользователя:")
    user_payload = {
        "nickname": "testuser",
        "email": "test@example.com"
    }
    send_message(producer, topic_name, "USER", "POST", user_payload)

    # Пример 2: Обновление пользователя
    print("\n2. Обновление пользователя:")
    user_update_payload = {
        "id": 1,
        "nickname": "updateduser",
        "email": "updated@example.com"
    }
    send_message(producer, topic_name, "USER", "PUT", user_update_payload)

    # Пример 3: Создание поста
    print("\n3. Создание поста:")
    post_payload = {
        "authorId": 1,
        "text": "Это тестовый пост из Kafka!"
    }
    send_message(producer, topic_name, "POST", "POST", post_payload)

    # Пример 4: Создание комментария
    print("\n4. Создание комментария:")
    comment_payload = {
        "postId": 1,
        "authorId": 1,
        "text": "Отличный пост!"
    }
    send_message(producer, topic_name, "COMMENT", "POST", comment_payload)

    # Пример 5: Удаление комментария
    print("\n5. Удаление комментария:")
    comment_delete_payload = {
        "postId": 1,
        "id": 1
    }
    send_message(producer, topic_name, "COMMENT", "DEL", comment_delete_payload)

    # Пример 6: Удаление поста
    print("\n6. Удаление поста:")
    send_message(producer, topic_name, "POST", "DEL", "1")

    # Пример 7: Удаление пользователя
    print("\n7. Удаление пользователя:")
    send_message(producer, topic_name, "USER", "DEL", "1")

    producer.flush()
    producer.close()
    print("\n" + "="*60)
    print("✓ Все сообщения отправлены успешно!")
    print("="*60)


def interactive_mode():
    """Интерактивный режим для отправки произвольных сообщений."""
    producer = create_producer()
    topic_name = 'entity-operations'

    print("\n" + "="*60)
    print("Интерактивный режим Kafka Producer")
    print("="*60)
    print("Введите 'quit' для выхода\n")

    while True:
        try:
            entity = input("Entity (USER/POST/COMMENT): ").strip()
            if entity.lower() == 'quit':
                break

            operation = input("Operation (POST/PUT/DEL): ").strip()
            if operation.lower() == 'quit':
                break

            print("Payload (JSON): ")
            payload_str = input().strip()
            if payload_str.lower() == 'quit':
                break

            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                payload = payload_str

            send_message(producer, topic_name, entity, operation, payload)
            print()

        except KeyboardInterrupt:
            print("\n\nВыход...")
            break

    producer.close()
    print("Goodbye!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        main()