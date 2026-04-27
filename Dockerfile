# Этап 1: Сборка (Build)
FROM gradle:8.5-jdk21-jammy AS build
WORKDIR /app

# Копируем gradle файлы для кэширования зависимостей
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle/ ./gradle/
COPY src/ ./src/

# Собираем приложение, пропуская тесты для скорости
RUN gradle build -x test

# Этап 2: Запуск (Run)
FROM eclipse-temurin:21-jre-jammy
WORKDIR /app

# Копируем JAR из этапа сборки
COPY --from=build /app/build/libs/*.jar app.jar

# Запускаем приложение
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]