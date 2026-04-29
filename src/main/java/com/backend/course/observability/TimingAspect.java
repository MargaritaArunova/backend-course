package com.backend.course.observability;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class TimingAspect {

    private final ObservabilityService observabilityService;

    /**
     * Измеряем время выполнения всех публичных методов контроллеров
     */
    @Around("execution(public * com.backend.course.controller..*(..))")
    public Object measureControllerTiming(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "Controller");
    }

    /**
     * Измеряем время выполнения всех методов репозиториев (обращение к БД)
     */
    @Around("execution(* com.backend.course.repository..*(..))")
    public Object measureRepositoryTiming(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "Repository");
    }

    /**
     * Измеряем время выполнения метода расчета статистики self-likes
     */
    @Around("execution(* com.backend.course.service.LikeService.getSelfLikeStats(..))")
    public Object measureSelfLikeStatsTiming(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "SelfLikeStats");
    }

    /**
     * Общий метод для измерения времени выполнения
     */
    private Object measureExecutionTime(ProceedingJoinPoint joinPoint, String category) throws Throwable {
        String className = joinPoint.getSignature().getDeclaringType().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        String fullMethodName = String.format("%s.%s.%s", category, className, methodName);

        long startTime = System.currentTimeMillis();
        try {
            return joinPoint.proceed();
        } finally {
            long executionTime = System.currentTimeMillis() - startTime;
            observabilityService.recordTiming(fullMethodName, executionTime);
            log.debug("Method {} executed in {} ms", fullMethodName, executionTime);
        }
    }
}