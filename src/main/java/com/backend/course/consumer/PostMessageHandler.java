package com.backend.course.consumer;

import com.backend.course.model.Post;
import com.backend.course.service.PostService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class PostMessageHandler implements MessageHandler {

    private final PostService postService;
    private final ObjectMapper objectMapper;

    @Override
    public void handle(String operation, String payload) {
        try {
            log.info("Processing POST operation: {} with payload: {}", operation, payload);

            switch (operation.toUpperCase()) {
                case "POST" -> handleCreate(payload);
                case "DEL", "DELETE" -> handleDelete(payload);
                default -> log.warn("Unknown operation: {}", operation);
            }
        } catch (Exception e) {
            log.error("Error processing POST message", e);
        }
    }

    private void handleCreate(String payload) throws Exception {
        JsonNode jsonNode = objectMapper.readTree(payload);
        Long authorId = jsonNode.get("authorId").asLong();
        String text = jsonNode.get("text").asText();

        Post created = postService.createPost(authorId, text);
        log.info("Created post: {}", created.getId());
    }

    private void handleDelete(String payload) throws Exception {
        try {
            Long postId = Long.parseLong(payload.trim());
            postService.deletePost(postId);
            log.info("Deleted post: {}", postId);
        } catch (NumberFormatException e) {
            JsonNode jsonNode = objectMapper.readTree(payload);
            Long postId = jsonNode.get("id").asLong();
            postService.deletePost(postId);
            log.info("Deleted post: {}", postId);
        }
    }

    @Override
    public String getSupportedEntity() {
        return "POST";
    }
}