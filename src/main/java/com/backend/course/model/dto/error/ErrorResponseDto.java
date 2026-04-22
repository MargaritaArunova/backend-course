package com.backend.course.model.dto.error;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@Schema
@AllArgsConstructor
public class ErrorResponseDto {

    private String code;

    private String message;
}