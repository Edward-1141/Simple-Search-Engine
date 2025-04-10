package com.edward1141.search.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SearchResult {
    private double score;
    private String title;
    private String url;
    private String lastModified;
    private int size;
    private Map<String, List<Integer>> wordPos;
    private Map<String, List<Integer>> titleWordPos;
    private List<String> parentLinks;
    private List<String> childLinks;
    private Map<String, Integer> keywords;
    private String body; // Added for body text snippet
} 