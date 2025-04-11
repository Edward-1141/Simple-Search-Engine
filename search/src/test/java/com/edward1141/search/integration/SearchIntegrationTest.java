package com.edward1141.search.integration;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class SearchIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void testFullSearchFlow() {
        String query = "test query";
        String url = "http://localhost:" + port + "/api/search?query=" + query;

        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        assertTrue(response.getStatusCode().is2xxSuccessful());
        assertNotNull(response.getBody());
    }

    @Test
    void testSearchWithInvalidInput() {
        String url = "http://localhost:" + port + "/api/search?query=";

        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        assertTrue(response.getStatusCode().is2xxSuccessful());
    }
} 