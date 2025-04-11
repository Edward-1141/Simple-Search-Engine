package com.edward1141.search.utils;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

@Data
public class SimilarityRetrieval {
    private double similarityScore;
    private Map<String, Set<Integer>> wordPositions = new HashMap<>();
}
