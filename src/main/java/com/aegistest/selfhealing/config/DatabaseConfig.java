package com.aegistest.selfhealing.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.sql.DataSource;
import java.sql.Connection;

@Configuration
public class DatabaseConfig {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConfig.class);

    @Value("${spring.datasource.url}")
    private String mysqlUrl;

    @Value("${spring.datasource.username}")
    private String mysqlUsername;

    @Value("${spring.datasource.password}")
    private String mysqlPassword;

    @Value("${spring.datasource.driver-class-name}")
    private String mysqlDriver;

    @Bean
    @Primary
    public DataSource dataSource() {
        log.info("Attempting to connect to primary database: {}", mysqlUrl);

        try {
            HikariConfig config = new HikariConfig();
            config.setJdbcUrl(mysqlUrl);
            config.setUsername(mysqlUsername);
            config.setPassword(mysqlPassword);
            config.setDriverClassName(mysqlDriver);
            config.setConnectionTimeout(2000); // 2 second timeout
            config.setMaximumPoolSize(10);
            config.setPoolName("AegisPrimaryPool");

            HikariDataSource ds = new HikariDataSource(config);

            // Test connection
            try (Connection conn = ds.getConnection()) {
                log.info("Successfully connected to primary MySQL database: {}", mysqlUrl);
                return ds;
            }
        } catch (Exception e) {
            log.warn("Could not connect to MySQL database ({}: {}). Falling back to embedded H2 database for resilient local execution.",
                    e.getClass().getSimpleName(), e.getMessage());

            HikariConfig h2Config = new HikariConfig();
            h2Config.setJdbcUrl("jdbc:h2:file:./data/aegis_test;MODE=MySQL;DATABASE_TO_LOWER=TRUE");
            h2Config.setUsername("sa");
            h2Config.setPassword("");
            h2Config.setDriverClassName("org.h2.Driver");
            h2Config.setConnectionTimeout(3000);
            h2Config.setPoolName("AegisH2FallbackPool");

            return new HikariDataSource(h2Config);
        }
    }
}
