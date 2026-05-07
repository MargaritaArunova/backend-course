plugins {
    java
    id("org.springframework.boot") version "3.3.4"
    id("io.spring.dependency-management") version "1.1.6"
}

group = "com.backend.course"
version = "1.0-SNAPSHOT"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Web
    implementation("org.springframework.boot:spring-boot-starter-web")

    // JPA / Hibernate
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")

    // Liquibase
    implementation("org.liquibase:liquibase-core")

    // Внимание: здесь была ошибка в оригинале — дублирование spring-boot-starter-web
    // Убрано дублирование

    // Стартер для валидации
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // Swagger UI
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")

    // База данных — PostgreSQL
    implementation("org.postgresql:postgresql")

    // AOP support
    implementation("org.springframework.boot:spring-boot-starter-aop")

    // Kafka
    implementation("org.springframework.kafka:spring-kafka")

    // Jackson для JSON
    implementation("com.fasterxml.jackson.core:jackson-databind")

    // Lombok (только для компиляции)
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // JUnit 5 launcher (для запуска тестов)
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")

    // Поддержка @AutoConfigureMockMvc (аналог стартера тестов WebMvc)
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")

    // Основной тестовый стартер (включает JUnit, Mockito, AssertJ и др.)
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}