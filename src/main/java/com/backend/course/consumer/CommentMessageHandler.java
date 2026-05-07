package com.backend.course.consumer;

import com.backend.course.model.Comment;
import com.backend.course.service.CommentService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class CommentMessageHandler implements MessageHandler {

    private final CommentService commentService;
    private final ObjectMapper objectMapper;

    @Override
    public void handle(String operation, String payload) {
        try {
            log.info("Processing COMMENT operation: {} with payload: {}", operation, payload);

            switch (operation.toUpperCase()) {
                case "POST" -> handleCreate(payload);
                case "DEL", "DELETE" -> handleDelete(payload);
                default -> log.warn("Unknown operation: {}", operation);
            }
        } catch (Exception e) {
            log.error("Error processing COMMENT message", e);
        }
    }

    private void handleCreate(String payload) throws Exception {
        JsonNode jsonNode = objectMapper.readTree(payload);
        Long postId = jsonNode.get("postId").asLong();
        Long authorId = jsonNode.get("authorId").asLong();
        String text = jsonNode.get("text").asText();

        Comment created = commentService.addComment(postId, authorId, text);
        log.info("Created comment: {}", created.getId());
    }

    private void handleDelete(String payload) throws Exception {
        JsonNode jsonNode = objectMapper.readTree(payload);
        Long postId = jsonNode.get("postId").asLong();
        Long commentId = jsonNode.get("id").asLong();

        commentService.deleteComment(postId, commentId);
        log.info("Deleted comment: {}", commentId);
    }

    @Override
    public String getSupportedEntity() {
        return "COMMENT";
    }
}