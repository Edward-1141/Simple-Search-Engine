package com.edward1141.search.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.util.FileCopyUtils;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;

@Configuration
public class StopwordsConfig {

    @Bean
    public Set<String> stopwords() {
        Set<String> stopwords = new HashSet<>();
        try {
            ClassPathResource resource = new ClassPathResource("stopwords/stopwords.txt");
            try (Reader reader = new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8)) {
                String content = FileCopyUtils.copyToString(reader);
                for (String word : content.split("\\s+")) {
                    stopwords.add(word.trim().toLowerCase());
                }
            }
        } catch (IOException e) {
            // Log the error but don't fail the application startup
            // The service will use an empty set of stopwords as fallback
            System.err.println("Failed to load stopwords file: " + e.getMessage());
        }
        return stopwords;
    }
} 