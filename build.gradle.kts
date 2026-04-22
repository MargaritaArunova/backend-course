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
    // implementation("org.springframework.boot:spring-boot-starter-data-jpa")

    // Liquibase
    // implementation("org.liquibase:liquibase-core")

    // Стартер для валидации
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // Добавляет Swagger UI
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")

    // Database driver (PostgreSQL)
    // implementation("org.postgresql:postgresql")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // JUnit 5 (Jupiter)
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")

    // Стартер для поддержки @AutoConfigureMockMvc в Spring Boot 4
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")

    // Тестовый стартер (JUnit 5, AssertJ, Mockito)
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}