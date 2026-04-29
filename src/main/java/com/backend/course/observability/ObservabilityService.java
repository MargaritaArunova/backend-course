package com.backend.course.observability;

import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.stream.Collectors;

@Slf4j
@Service
public class ObservabilityService {

    @Value("${observability.window.short:10}")
    private int shortWindowSeconds;

    @Value("${observability.window.medium:30}")
    private int mediumWindowSeconds;

    @Value("${observability.window.long:60}")
    private int longWindowSeconds;

    // Структура для хранения замеров времени
    private final Map<String, Queue<TimingRecord>> timingData = new ConcurrentHashMap<>();

    /**
     * Записывает время выполнения метода
     */
    public void recordTiming(String methodName, long executionTimeMs) {
        timingData.computeIfAbsent(methodName, k -> new ConcurrentLinkedQueue<>())
                .add(new TimingRecord(Instant.now(), executionTimeMs));
    }

    /**
     * Получить статистику за последние N секунд для конкретного метода
     */
    public MethodStats getStats(String methodName, int windowSeconds) {
        Queue<TimingRecord> records = timingData.get(methodName);
        if (records == null || records.isEmpty()) {
            return new MethodStats(methodName, 0, 0, 0, 0, 0);
        }

        Instant cutoff = Instant.now().minusSeconds(windowSeconds);
        List<Long> recentTimings = records.stream()
                .filter(r -> r.timestamp.isAfter(cutoff))
                .map(r -> r.executionTimeMs)
                .toList();

        if (recentTimings.isEmpty()) {
            return new MethodStats(methodName, 0, 0, 0, 0, 0);
        }

        long count = recentTimings.size();
        long sum = recentTimings.stream().mapToLong(Long::longValue).sum();
        double avg = (double) sum / count;
        long min = recentTimings.stream().mapToLong(Long::longValue).min().orElse(0);
        long max = recentTimings.stream().mapToLong(Long::longValue).max().orElse(0);

        return new MethodStats(methodName, count, avg, min, max, windowSeconds);
    }

    /**
     * Получить статистику для всех методов за указанное окно времени
     */
    public Map<String, MethodStats> getAllStats(int windowSeconds) {
        return timingData.keySet().stream()
                .collect(Collectors.toMap(
                        method -> method,
                        method -> getStats(method, windowSeconds)
                ));
    }

    /**
     * Scheduled метод для очистки старых данных и вывода статистики
     */
    @Scheduled(fixedDelayString = "${observability.cleanup.interval:10000}")
    public void cleanupAndLogStats() {
        Instant cutoff = Instant.now().minusSeconds(longWindowSeconds);

        // Очистка старых записей
        timingData.forEach((methodName, records) -> {
            records.removeIf(record -> record.timestamp.isBefore(cutoff));
        });

        // Вывод статистики
        log.info("=== Observability Statistics ===");
        logStatsForWindow(shortWindowSeconds, "SHORT");
        logStatsForWindow(mediumWindowSeconds, "MEDIUM");
        logStatsForWindow(longWindowSeconds, "LONG");
        log.info("================================");
    }

    private void logStatsForWindow(int windowSeconds, String label) {
        log.info("--- {} window ({} seconds) ---", label, windowSeconds);
        Map<String, MethodStats> stats = getAllStats(windowSeconds);

        if (stats.isEmpty() || stats.values().stream().allMatch(s -> s.getCount() == 0)) {
            log.info("No data available");
            return;
        }

        stats.forEach((method, stat) -> {
            if (stat.getCount() > 0) {
                log.info("{}: count={}, avg={:.2f}ms, min={}ms, max={}ms",
                        method, stat.getCount(), stat.getAvgMs(), stat.getMinMs(), stat.getMaxMs());
            }
        });
    }

    /**
     * Запись времени выполнения
     */
    private record TimingRecord(Instant timestamp, long executionTimeMs) {
    }

    /**
     * Статистика по методу
     */
    @Getter
    public static class MethodStats {
        private final String methodName;
        private final long count;
        private final double avgMs;
        private final long minMs;
        private final long maxMs;
        private final int windowSeconds;

        public MethodStats(String methodName, long count, double avgMs, long minMs, long maxMs, int windowSeconds) {
            this.methodName = methodName;
            this.count = count;
            this.avgMs = avgMs;
            this.minMs = minMs;
            this.maxMs = maxMs;
            this.windowSeconds = windowSeconds;
        }
    }
}