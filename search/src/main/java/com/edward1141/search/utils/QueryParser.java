package com.edward1141.search.utils;
import lombok.Getter;

import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QueryParser {
    private final Pattern quotePattern = Pattern.compile("\"([^\"]*)\"");

    @Getter
    public static class QueryParseResult {
        private final List<String> queryTerms = new ArrayList<>();
        private final List<String> quotedTerms = new ArrayList<>();
    }

    public QueryParseResult parse(String query) {
        QueryParseResult result = new QueryParseResult();
        Matcher quoteMatcher = quotePattern.matcher(query);

        String quotedString = "";

        // Find first quoted terms
        if (quoteMatcher.find()) {
            quotedString = quoteMatcher.group(1).replaceAll("[^\\w\\s]", "").toLowerCase();
        }

        StringTokenizer quoteTokenizer = new StringTokenizer(quotedString, " \t\n\r\f");
        while (quoteTokenizer.hasMoreTokens()) {
            String token = quoteTokenizer.nextToken();
            if (!token.isEmpty()) {
                result.getQuotedTerms().add(token);
            }
        }

        String cleanedQuery = query.replaceAll("[^\\w\\s]", "").toLowerCase();
        StringTokenizer tokenizer = new StringTokenizer(cleanedQuery, " \t\n\r\f");
        while (tokenizer.hasMoreTokens()) {
            String token = tokenizer.nextToken();
            if (!token.isEmpty()) {
                result.getQueryTerms().add(token);
            }
        }

        return result;
    }
}
