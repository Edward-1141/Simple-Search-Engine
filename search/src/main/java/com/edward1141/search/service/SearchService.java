package com.edward1141.search.service;

import com.edward1141.search.model.SearchRequest;
import com.edward1141.search.model.SearchResponse;
import com.edward1141.search.model.SearchResult;
import com.edward1141.search.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class SearchService {
    private final WordListRepository wordListRepository;
    private final UrlListRepository urlListRepository;
    private final ParentChildRepository parentChildRepository;
    private final InvertedIndexRepository invertedIndexRepository;
    private final TitleInvertedIndexRepository titleInvertedIndexRepository;
    private final RawInvertedIndexRepository rawInvertedIndexRepository;
    private final RawTitleInvertedIndexRepository rawTitleInvertedIndexRepository;
    private final StemmedRawInvertedIndexRepository stemmedRawInvertedIndexRepository;
    private final StemmedRawTitleInvertedIndexRepository stemmedRawTitleInvertedIndexRepository;
    private final ForwardIndexRepository forwardIndexRepository;
    private final UrlBodyRepository urlBodyRepository;
    
    private final Set<String> stopwords;
    private final double titleWeight;
    private final double bodyWeight;
    private final double pageRankWeight;
    
    @Autowired
    public SearchService(
            WordListRepository wordListRepository,
            UrlListRepository urlListRepository,
            ParentChildRepository parentChildRepository,
            InvertedIndexRepository invertedIndexRepository,
            TitleInvertedIndexRepository titleInvertedIndexRepository,
            RawInvertedIndexRepository rawInvertedIndexRepository,
            RawTitleInvertedIndexRepository rawTitleInvertedIndexRepository,
            StemmedRawInvertedIndexRepository stemmedRawInvertedIndexRepository,
            StemmedRawTitleInvertedIndexRepository stemmedRawTitleInvertedIndexRepository,
            ForwardIndexRepository forwardIndexRepository,
            UrlBodyRepository urlBodyRepository,
            Set<String> stopwords) {
        this.wordListRepository = wordListRepository;
        this.urlListRepository = urlListRepository;
        this.parentChildRepository = parentChildRepository;
        this.invertedIndexRepository = invertedIndexRepository;
        this.titleInvertedIndexRepository = titleInvertedIndexRepository;
        this.rawInvertedIndexRepository = rawInvertedIndexRepository;
        this.rawTitleInvertedIndexRepository = rawTitleInvertedIndexRepository;
        this.stemmedRawInvertedIndexRepository = stemmedRawInvertedIndexRepository;
        this.stemmedRawTitleInvertedIndexRepository = stemmedRawTitleInvertedIndexRepository;
        this.forwardIndexRepository = forwardIndexRepository;
        this.urlBodyRepository = urlBodyRepository;
        this.stopwords = stopwords;
        
        // FIXME: Magic Default values
        this.titleWeight = 4.0;
        this.bodyWeight = 1.0;
        this.pageRankWeight = 0.2;
    }
    
    private Set<String> loadStopwords() {
        // In a real implementation, load from a file
        // For now, return an empty set
        return new HashSet<>();
    }
    
    public SearchResponse search(SearchRequest request) {
        long startTime = System.currentTimeMillis();
        
        List<String> queryTerms;
        List<String> phraseTerms = null;
        
        if (request.getQuery().contains("\"")) {
            // Handle phrase search
            String[] parts = request.getQuery().split("\"");
            if (parts.length >= 3) {
                phraseTerms = parse(parts[1]);
                if (!request.isRawMatchPhrase()) {
                    phraseTerms = removeStopwords(stem(phraseTerms));
                } else if (request.isStemForRaw()) {
                    phraseTerms = stem(phraseTerms);
                }

            }
        }
        queryTerms = removeStopwords(stem(parse(request.getQuery())));

        List<SearchResult> results = _search(
                queryTerms,
                phraseTerms,
                request.isRawMatchPhrase(),
                request.isStemForRaw(),
                request.isMatchInTitle(),
                request.getPhraseSearchDistance(),
                request.isWithPageRank()
        );
        
        long endTime = System.currentTimeMillis();
        
        return SearchResponse.builder()
                .results(results)
                .stemmedQuery(queryTerms)
                .totalResults(results.size())
                .searchTimeMs(endTime - startTime)
                .build();
    }
    
    private List<String> parse(String s) {
        // Remove punctuation and convert to lowercase
        String cleanedText = s.replaceAll("[^\\w\\s]", "").toLowerCase();
        
        // Use StringTokenizer to split by whitespace
        StringTokenizer tokenizer = new StringTokenizer(cleanedText, " \t\n\r\f");
        List<String> tokens = new ArrayList<>();
        
        while (tokenizer.hasMoreTokens()) {
            String token = tokenizer.nextToken();
            if (!token.isEmpty()) {
                tokens.add(token);
            }
        }
        
        return tokens;
    }
    
    private List<String> stem(List<String> words) {
        // In a real implementation, use a stemmer like PorterStemmer
        // For now, just return the words as is
        return words;
    }
    
    private List<String> removeStopwords(List<String> words) {
        return words.stream()
                .filter(word -> !stopwords.contains(word))
                .collect(Collectors.toList());
    }
    
    private boolean isContainPhrase(Set<Integer> lastWordPositions, Set<Integer> nextWordPositions, int distance) {
        for (int i = 1; i <= distance; i++) {
            for (Integer lastPos : lastWordPositions) {
                if (nextWordPositions.contains(lastPos + i)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    private Set<Integer> filtering(List<String> phrase, boolean raw, String table, int phraseSearchDistance, boolean stemForRaw) {
        Map<Integer, List<Set<Integer>>> uidPositionList = new HashMap<>();
        
        for (int idx = 0; idx < phrase.size(); idx++) {
            String word = phrase.get(idx);
            Integer wid = wordListRepository.findWidByWord(word);
            
            if (wid == null) {
                return new HashSet<>(); // No URL contains the phrase
            }
            
            Object[] result;
            if (table.equals("body")) {
                if (raw && stemForRaw) {
                    result = rawInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else if (raw && !stemForRaw) {
                    result = stemmedRawInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else {
                    result = invertedIndexRepository.getInvertedIndexPosition(wid);
                }
            } else { // table == "title"
                if (raw && stemForRaw) {
                    result = rawTitleInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else if (raw && !stemForRaw) {
                    result = stemmedRawTitleInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else {
                    result = titleInvertedIndexRepository.getInvertedIndexPosition(wid);
                }
            }
            
            if (result == null || result.length < 2) {
                return new HashSet<>();
            }
            
            Integer count = (Integer) result[0];
            @SuppressWarnings("unchecked")
            Map<Integer, Set<Integer>> bodyQuery = (Map<Integer, Set<Integer>>) result[1];
            
            if (idx != 0) {
                // Filter URLs that contain all words in the phrase
                uidPositionList.keySet().removeIf(urlId -> !bodyQuery.containsKey(urlId));
            }
            
            for (Map.Entry<Integer, Set<Integer>> entry : bodyQuery.entrySet()) {
                Integer urlId = entry.getKey();
                Set<Integer> wordPositions = entry.getValue();
                
                if (idx == 0 || (uidPositionList.containsKey(urlId) && 
                        isContainPhrase(uidPositionList.get(urlId).get(idx-1), wordPositions, phraseSearchDistance))) {
                    uidPositionList.computeIfAbsent(urlId, k -> new ArrayList<>()).add(wordPositions);
                } else {
                    uidPositionList.remove(urlId);
                }
            }
        }
        
        return new HashSet<>(uidPositionList.keySet());
    }
    
    private Set<Integer> filtering(List<String> phrase, boolean matchInTitle, boolean raw, boolean stemForRaw, int phraseSearchDistance) {
        if (!raw) {
            phrase = stem(phrase);
        }
        
        if (matchInTitle) {
            return filtering(phrase, raw, "title", phraseSearchDistance, stemForRaw);
        } else {
            Set<Integer> titleResults = filtering(phrase, raw, "title", phraseSearchDistance, stemForRaw);
            Set<Integer> bodyResults = filtering(phrase, raw, "body", phraseSearchDistance, stemForRaw);
            
            Set<Integer> combinedResults = new HashSet<>(titleResults);
            combinedResults.addAll(bodyResults);
            return combinedResults;
        }
    }
    
    private Map<Integer, Object[]> _cosineSimilarity(List<String> query, String invertedIndexTable, Set<Integer> filteredUrl) {
        Map<Integer, Object[]> innerProducts = new HashMap<>();
        double[] queryVector = new double[query.size()];
        
        for (int idx = 0; idx < query.size(); idx++) {
            String keyWord = query.get(idx);
            Integer wid = wordListRepository.findWidByWord(keyWord);
            
            if (wid == null) {
                continue;
            }
            
            Object[] result;
            if (invertedIndexTable.equals("invertedIndex")) {
                result = invertedIndexRepository.getInvertedIndexFullInfo(wid);
            } else { // titleInvertedIndex
                result = titleInvertedIndexRepository.getInvertedIndexFullInfo(wid);
            }
            
            if (result == null || result.length < 2) {
                continue;
            }
            
            Integer count = (Integer) result[0];
            @SuppressWarnings("unchecked")
            Map<Integer, Object[]> bodyQuery = (Map<Integer, Object[]>) result[1];
            
            if (!bodyQuery.isEmpty()) {
                Object[] firstEntry = bodyQuery.values().iterator().next();
                queryVector[idx] = (Double) firstEntry[3]; // idf value
            }
            
            for (Map.Entry<Integer, Object[]> entry : bodyQuery.entrySet()) {
                Integer urlId = entry.getKey();
                
                // Filter out URLs not in the filtered set
                if (filteredUrl != null && !filteredUrl.contains(urlId)) {
                    continue;
                }
                
                Object[] values = entry.getValue();
                Double tfNorm = (Double) values[2];
                Double idf = (Double) values[3];
                @SuppressWarnings("unchecked")
                List<Integer> positions = (List<Integer>) values[4];
                
                Double documentWeight = urlListRepository.getDocumentWeight(urlId);
                if (documentWeight == null) {
                    documentWeight = 1.0;
                }
                
                Object[] innerProduct = innerProducts.computeIfAbsent(urlId, k -> new Object[]{0.0, new HashMap<String, Set<Integer>>()});
                innerProduct[0] = (Double) innerProduct[0] + getTermWeight(tfNorm, idf) / documentWeight;
                
                @SuppressWarnings("unchecked")
                Map<String, Set<Integer>> wordPositions = (Map<String, Set<Integer>>) innerProduct[1];
                wordPositions.computeIfAbsent(keyWord, k -> new HashSet<>()).addAll(positions);
            }
        }
        
        // Normalize query vector
        double queryLength = 0.0;
        for (double v : queryVector) {
            queryLength += v * v;
        }
        queryLength = Math.sqrt(queryLength);
        
        // Normalize scores
        for (Object[] innerProduct : innerProducts.values()) {
            innerProduct[0] = (Double) innerProduct[0] / queryLength;
        }
        
        return innerProducts;
    }
    
    private double getTermWeight(double tfNorm, double idf) {
        return tfNorm * idf;
    }
    
    private List<SearchResult> _search(List<String> query, List<String> phrase, boolean rawMatchPhrase, 
                                      boolean stemForRaw, boolean matchInTitle, int phraseSearchDistance, 
                                      boolean withPageRank) {
        Map<Integer, SearchResult> results = new HashMap<>();
        
        Set<Integer> filteredUrl = null;
        if (phrase != null && !phrase.isEmpty()) {
            filteredUrl = filtering(phrase, matchInTitle, rawMatchPhrase, stemForRaw, phraseSearchDistance);
        }
        
        Map<Integer, Object[]> bodyInnerProducts = _cosineSimilarity(query, "invertedIndex", filteredUrl);
        Map<Integer, Object[]> titleInnerProducts = _cosineSimilarity(query, "titleInvertedIndex", filteredUrl);
        
        // Process body results
        for (Map.Entry<Integer, Object[]> entry : bodyInnerProducts.entrySet()) {
            Integer urlId = entry.getKey();
            Object[] innerProduct = entry.getValue();
            Double score = (Double) innerProduct[0] * bodyWeight;
            
            @SuppressWarnings("unchecked")
            Map<String, Set<Integer>> wordPositions = (Map<String, Set<Integer>>) innerProduct[1];
            
            SearchResult result = results.computeIfAbsent(urlId, k -> new SearchResult());
            result.setScore(result.getScore() + score);
            result.setWordPos(new HashMap<>());
            for (Map.Entry<String, Set<Integer>> wordPos : wordPositions.entrySet()) {
                result.getWordPos().put(wordPos.getKey(), new ArrayList<>(wordPos.getValue()));
            }
            
            // Get URL info
            String url = urlListRepository.findUrlByUid(urlId);
            Object[] urlInfo = urlListRepository.getUrlInfo(urlId);
            
            result.setUrl(url);
            if (urlInfo != null && urlInfo.length >= 3) {
                result.setTitle((String) urlInfo[0]);
                result.setLastModified((String) urlInfo[1]);
                result.setSize((Integer) urlInfo[2]);
            }
            
            // Get parent and child links
            List<Integer> parentIds = parentChildRepository.findParentIdsByChildId(urlId);
            List<Integer> childIds = parentChildRepository.findChildIdsByParentId(urlId);
            
            result.setParentLinks(parentIds.stream()
                    .map(urlListRepository::findUrlByUid)
                    .collect(Collectors.toList()));
            
            result.setChildLinks(childIds.stream()
                    .map(urlListRepository::findUrlByUid)
                    .collect(Collectors.toList()));
            
            // Get keywords
            Object[] forwardIndexHead = forwardIndexRepository.getForwardIndexHead(urlId);
            if (forwardIndexHead != null && forwardIndexHead.length >= 2) {
                @SuppressWarnings("unchecked")
                Map<String, Integer> keywords = (Map<String, Integer>) forwardIndexHead[1];
                result.setKeywords(keywords);
            }
        }
        
        // Process title results
        for (Map.Entry<Integer, Object[]> entry : titleInnerProducts.entrySet()) {
            Integer urlId = entry.getKey();
            Object[] innerProduct = entry.getValue();
            Double score = (Double) innerProduct[0] * titleWeight;
            
            @SuppressWarnings("unchecked")
            Map<String, Set<Integer>> wordPositions = (Map<String, Set<Integer>>) innerProduct[1];
            
            SearchResult result = results.computeIfAbsent(urlId, k -> new SearchResult());
            result.setScore(result.getScore() + score);
            result.setTitleWordPos(new HashMap<>());
            for (Map.Entry<String, Set<Integer>> wordPos : wordPositions.entrySet()) {
                result.getTitleWordPos().put(wordPos.getKey(), new ArrayList<>(wordPos.getValue()));
            }
            
            // Get URL info if not already set
            if (result.getUrl() == null) {
                String url = urlListRepository.findUrlByUid(urlId);
                Object[] urlInfo = urlListRepository.getUrlInfo(urlId);
                
                result.setUrl(url);
                if (urlInfo != null && urlInfo.length >= 3) {
                    result.setTitle((String) urlInfo[0]);
                    result.setLastModified((String) urlInfo[1]);
                    result.setSize((Integer) urlInfo[2]);
                }
                
                // Get parent and child links
                List<Integer> parentIds = parentChildRepository.findParentIdsByChildId(urlId);
                List<Integer> childIds = parentChildRepository.findChildIdsByParentId(urlId);
                
                result.setParentLinks(parentIds.stream()
                        .map(urlListRepository::findUrlByUid)
                        .collect(Collectors.toList()));
                
                result.setChildLinks(childIds.stream()
                        .map(urlListRepository::findUrlByUid)
                        .collect(Collectors.toList()));
                
                // Get keywords
                Object[] forwardIndexHead = forwardIndexRepository.getForwardIndexHead(urlId);
                if (forwardIndexHead != null && forwardIndexHead.length >= 2) {
                    @SuppressWarnings("unchecked")
                    Map<String, Integer> keywords = (Map<String, Integer>) forwardIndexHead[1];
                    result.setKeywords(keywords);
                }
            }
        }
        
        // Add page rank score
        if (withPageRank) {
            for (SearchResult result : results.values()) {
                Integer urlId = urlListRepository.findUidByUrl(result.getUrl());
                if (urlId != null) {
                    Double pageRankScore = urlListRepository.getPageRankScore(urlId);
                    if (pageRankScore != null) {
                        result.setScore(result.getScore() + pageRankWeight * pageRankScore);
                    }
                }
            }
        }
        
        // Sort results by score
        List<SearchResult> sortedResults = new ArrayList<>(results.values());
        sortedResults.sort((a, b) -> Double.compare(b.getScore(), a.getScore()));
        
        // Add body snippets for top 5 results
        for (int i = 0; i < Math.min(5, sortedResults.size()); i++) {
            SearchResult result = sortedResults.get(i);
            Integer urlId = urlListRepository.findUidByUrl(result.getUrl());
            if (urlId != null) {
                String body = urlBodyRepository.getUrlBody(urlId);
                if (body != null && !result.getWordPos().isEmpty()) {
                    // Find the earliest position of any query word
                    int minIndex = Integer.MAX_VALUE;
                    for (String queryWord : result.getWordPos().keySet()) {
                        int startIndex = body.toLowerCase().indexOf(queryWord.toLowerCase());
                        if (startIndex >= 0 && startIndex < minIndex) {
                            minIndex = startIndex;
                        }
                    }
                    
                    // Extract a snippet
                    if (minIndex < Integer.MAX_VALUE) {
                        int endIndex = Math.min(minIndex + 200, body.length());
                        result.setBody(body.substring(minIndex, endIndex));
                    } else {
                        result.setBody(body.substring(0, Math.min(200, body.length())));
                    }
                }
            }
        }
        
        return sortedResults;
    }
}
