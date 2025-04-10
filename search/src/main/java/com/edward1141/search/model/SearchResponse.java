package com.edward1141.search.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SearchResponse {
    private List<SearchResult> results;
    private List<String> stemmedQuery;
    private int totalResults;
    private long searchTimeMs;
} 