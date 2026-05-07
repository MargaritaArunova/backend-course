package com.backend.course.consumer;

import com.backend.course.model.dto.KafkaMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class EntityOperationsConsumer {

    private final List<MessageHandler> messageHandlers;
    private final ObjectMapper objectMapper;
    private final Map<String, MessageHandler> handlerMap = new HashMap<>();

    @PostConstruct
    public void init() {
        messageHandlers.forEach(handler ->
                handlerMap.put(handler.getSupportedEntity().toUpperCase(), handler)
        );
        log.info("Initialized {} message handlers: {}", handlerMap.size(), handlerMap.keySet());
    }

    @KafkaListener(
            topics = "${kafka.topic.name}",
            groupId = "${spring.kafka.consumer.group-id}",
            concurrency = "${kafka.listener.concurrency}"
    )
    public void consume(String message) {
        try {
            log.info("Received message: {}", message);

            KafkaMessage kafkaMessage = objectMapper.readValue(message, KafkaMessage.class);

            String entity = kafkaMessage.getEntity();
            String operation = kafkaMessage.getOperation();
            String payload = kafkaMessage.getPayload();

            if (entity == null || operation == null) {
                log.error("Invalid message format: entity or operation is null");
                return;
            }

            MessageHandler handler = handlerMap.get(entity.toUpperCase());

            if (handler == null) {
                log.warn("No handler found for entity: {}", entity);
                return;
            }

            handler.handle(operation, payload);
            log.info("Successfully processed message for entity: {} with operation: {}", entity, operation);

        } catch (Exception e) {
            log.error("Error consuming message: {}", message, e);
        }
    }
}