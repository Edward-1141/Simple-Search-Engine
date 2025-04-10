package com.edward1141.search.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SearchRequest {
    private String query;
    private boolean rawMatchPhrase;
    private boolean stemForRaw;
    private boolean matchInTitle;
    private int phraseSearchDistance;
    private boolean withPageRank;
} 