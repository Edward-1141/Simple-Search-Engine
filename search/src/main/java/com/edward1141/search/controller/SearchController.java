package com.edward1141.search.controller;

import com.edward1141.search.model.SearchRequest;
import com.edward1141.search.model.SearchResponse;
import com.edward1141.search.service.SearchService;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class SearchController {

    private final SearchService searchService;
    private final Logger logger = LoggerFactory.getLogger(SearchController.class);

    @Autowired
    public SearchController(SearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> search(
            @RequestParam(value = "query", required = false) String query,
            @RequestParam(value = "phrase-search-options", defaultValue = "0") String phraseSearchOptions,
            @RequestParam(value = "match-in-title", required = false) String matchInTitle,
            @RequestParam(value = "page-rank", required = false) String pageRank,
            @RequestParam(value = "phrase-search-distance", defaultValue = "1") String phraseSearchDistance,
            @RequestParam(value = "skip-history", required = false) String skipHistory,
            @RequestParam(value = "exclude-words", required = false) String excludeWords,
            @RequestParam(value = "date-start", required = false) String dateStart,
            @RequestParam(value = "time-start", required = false) String timeStart,
            @RequestParam(value = "date-end", required = false) String dateEnd,
            @RequestParam(value = "time-end", required = false) String timeEnd) throws JsonProcessingException {


        long startTime = System.currentTimeMillis();

        // Default response if no query is provided
        if (query == null || query.isEmpty()) {
            Map<String, Object> response = new HashMap<>();
            response.put("history", new String[0]);
            response.put("options", createDefaultOptions());
            return ResponseEntity.ok(response);
        }

        // Parse options
        boolean rawMatchPhrase = false;
        boolean stemForRaw = false;
        boolean matchInTitleFlag = matchInTitle != null && matchInTitle.equals("on");
        boolean withPageRank = pageRank != null && pageRank.equals("on");
        int phraseSearchDistanceValue = Integer.parseInt(phraseSearchDistance);

        // Set phrase search options based on the parameter
        if (phraseSearchOptions.equals("1")) {
            rawMatchPhrase = true;
            stemForRaw = true;
        } else if (phraseSearchOptions.equals("2")) {
            rawMatchPhrase = true;
            stemForRaw = false;
        }

        // Create search request
        SearchRequest searchRequest = SearchRequest.builder()
                .query(query)
                .rawMatchPhrase(rawMatchPhrase)
                .stemForRaw(stemForRaw)
                .matchInTitle(matchInTitleFlag)
                .phraseSearchDistance(phraseSearchDistanceValue)
                .withPageRank(withPageRank)
                .build();

        // Perform search
        SearchResponse searchResponse = searchService.search(searchRequest);

        // Create response
        Map<String, Object> response = new HashMap<>();
        response.put("query", query);
        response.put("results", searchResponse.getResults());
        response.put("time", String.format("%.4f", (System.currentTimeMillis() - startTime) / 1000.0));
        response.put("options", createOptions(phraseSearchOptions, matchInTitle, pageRank, phraseSearchDistance, 
                skipHistory, excludeWords, dateStart, timeStart, dateEnd, timeEnd));
        response.put("stemmed_query", searchResponse.getStemmedQuery());
//        response.put("history", new String[0]); // TODO: Implement history

        return ResponseEntity.ok(response);
    }

    @GetMapping("/clear-history")
    public ResponseEntity<Map<String, Object>> clearHistory(
            @RequestParam(value = "item", required = false) String item) {
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        
        // TODO: Implement history clearing logic
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/check-db")
    public ResponseEntity<Map<String, Object>> checkDatabase() {
        Map<String, Object> response = new HashMap<>();
        try {
            // Try to get a count of records from wordList table
            long count = searchService.getWordListCount();
            response.put("success", true);
            response.put("message", "Database connection successful");
            response.put("wordList_count", count);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Database error: " + e.getMessage());
        }
        return ResponseEntity.ok(response);
    }

    private Map<String, Object> createDefaultOptions() {
        Map<String, Object> options = new HashMap<>();
        options.put("phrase-search-options", "0");
        options.put("match-in-title", null);
        options.put("page-rank", true);
        options.put("phrase-search-distance", 1);
        options.put("skip-history", null);
        options.put("exclude-words", null);
        options.put("date-start", null);
        options.put("time-start", null);
        options.put("date-end", null);
        options.put("time-end", null);
        return options;
    }

    private Map<String, Object> createOptions(String phraseSearchOptions, String matchInTitle, String pageRank,
                                             String phraseSearchDistance, String skipHistory, String excludeWords,
                                             String dateStart, String timeStart, String dateEnd, String timeEnd) {
        Map<String, Object> options = new HashMap<>();
        options.put("phrase-search-options", phraseSearchOptions);
        options.put("match-in-title", matchInTitle);
        options.put("page-rank", pageRank);
        options.put("phrase-search-distance", phraseSearchDistance);
        options.put("skip-history", skipHistory);
        options.put("exclude-words", excludeWords);
        options.put("date-start", dateStart);
        options.put("time-start", timeStart);
        options.put("date-end", dateEnd);
        options.put("time-end", timeEnd);
        return options;
    }
} 