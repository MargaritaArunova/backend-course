package com.backend.course.controller;

import com.backend.course.observability.ObservabilityService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/observability")
@RequiredArgsConstructor
public class ObservabilityController {

    private final ObservabilityService observabilityService;

    /**
     * Получить статистику за короткое окно (по умолчанию 10 секунд)
     */
    @GetMapping("/stats/short")
    public Map<String, ObservabilityService.MethodStats> getShortWindowStats() {
        return observabilityService.getAllStats(10);
    }

    /**
     * Получить статистику за среднее окно (по умолчанию 30 секунд)
     */
    @GetMapping("/stats/medium")
    public Map<String, ObservabilityService.MethodStats> getMediumWindowStats() {
        return observabilityService.getAllStats(30);
    }

    /**
     * Получить статистику за длинное окно (по умолчанию 60 секунд)
     */
    @GetMapping("/stats/long")
    public Map<String, ObservabilityService.MethodStats> getLongWindowStats() {
        return observabilityService.getAllStats(60);
    }

    /**
     * Получить статистику за произвольное окно времени
     */
    @GetMapping("/stats")
    public Map<String, ObservabilityService.MethodStats> getStats(
            @RequestParam(defaultValue = "10") int windowSeconds) {
        return observabilityService.getAllStats(windowSeconds);
    }
}