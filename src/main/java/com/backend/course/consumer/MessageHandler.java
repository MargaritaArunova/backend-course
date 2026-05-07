package com.backend.course.consumer;

public interface MessageHandler {
    void handle(String operation, String payload);
    String getSupportedEntity();
}