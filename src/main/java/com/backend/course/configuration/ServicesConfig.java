package com.backend.course.configuration;

import com.backend.course.service.StatisticsService;
import com.backend.course.service.UserService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ServicesConfig {

    @Bean
    @ConditionalOnProperty(prefix = "statistics", name = "service", havingValue = "console10000")
    StatisticsService statisticsService2000(UserService userService){
        return new StatisticsService(10000, userService);
    }

    @Bean
    @ConditionalOnProperty(prefix = "statistics", name = "service", havingValue = "console2000")
    StatisticsService statisticsService1000(UserService userService){
        return new StatisticsService(2000, userService);
    }
}
