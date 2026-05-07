package com.backend.course.model.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class KafkaMessage {

    @JsonProperty("entity")
    private String entity;

    @JsonProperty("operation")
    private String operation;

    @JsonProperty("payload")
    private String payload;
}