package com.backend.course.consumer;

import com.backend.course.model.User;
import com.backend.course.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class UserMessageHandler implements MessageHandler {

    private final UserService userService;
    private final ObjectMapper objectMapper;

    @Override
    public void handle(String operation, String payload) {
        try {
            log.info("Processing USER operation: {} with payload: {}", operation, payload);

            switch (operation.toUpperCase()) {
                case "POST" -> handleCreate(payload);
                case "PUT" -> handleUpdate(payload);
                case "DEL", "DELETE" -> handleDelete(payload);
                default -> log.warn("Unknown operation: {}", operation);
            }
        } catch (Exception e) {
            log.error("Error processing USER message", e);
        }
    }

    private void handleCreate(String payload) throws Exception {
        User user = objectMapper.readValue(payload, User.class);
        User created = userService.saveUser(user);
        log.info("Created user: {}", created.getId());
    }

    private void handleUpdate(String payload) throws Exception {
        User user = objectMapper.readValue(payload, User.class);
        if (user.getId() != null) {
            User updated = userService.updateUser(user.getId().toString(), user);
            log.info("Updated user: {}", updated.getId());
        } else {
            log.warn("Cannot update user without ID");
        }
    }

    private void handleDelete(String payload) throws Exception {
        // Expecting payload to be just the ID or JSON with id field
        try {
            Long userId = Long.parseLong(payload.trim());
            userService.deleteUser(userId.toString());
            log.info("Deleted user: {}", userId);
        } catch (NumberFormatException e) {
            User user = objectMapper.readValue(payload, User.class);
            if (user.getId() != null) {
                userService.deleteUser(user.getId().toString());
                log.info("Deleted user: {}", user.getId());
            }
        }
    }

    @Override
    public String getSupportedEntity() {
        return "USER";
    }
}