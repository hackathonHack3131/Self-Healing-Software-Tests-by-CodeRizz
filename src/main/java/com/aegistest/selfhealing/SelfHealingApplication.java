package com.aegistest.selfhealing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class SelfHealingApplication {

    public static void main(String[] args) {
        SpringApplication.run(SelfHealingApplication.class, args);
    }
}
