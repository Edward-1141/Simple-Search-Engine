package com.edward1141.search.service;

import com.edward1141.search.entity.UrlList;
import com.edward1141.search.model.SearchRequest;
import com.edward1141.search.model.SearchResponse;
import com.edward1141.search.model.SearchResult;
import com.edward1141.search.repository.*;
import com.edward1141.search.utils.IndexParser;
import com.edward1141.search.utils.IndexParser.*;
import com.edward1141.search.utils.QueryParser;
import com.edward1141.search.utils.QueryParser.QueryParseResult;
import com.edward1141.search.utils.SimilarityRetrieval;
import com.fasterxml.jackson.core.JsonProcessingException;
import opennlp.tools.stemmer.PorterStemmer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;


// TODO: use Enum for String
// TODO: refactor refactor to don't remove count for inverted index
// TODO: fixed the Object[] and create classes for them
// TODO: Remove useless wordPos and titleWordPos

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
    private final PorterStemmer stemmer;
    private final IndexParser indexParser;
    private static final Logger logger = LoggerFactory.getLogger(SearchService.class);
    
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
        this.titleWeight = 3.0;
        this.bodyWeight = 1.0;
        this.pageRankWeight = 0.2;
        
        // Initialize the stemmer once
        this.stemmer = new PorterStemmer();
        this.indexParser = new IndexParser();
    }

    public SearchResponse search(SearchRequest request) throws JsonProcessingException {
        logger.info("Search request: {}", request);
        long startTime = System.currentTimeMillis();

        QueryParseResult queryParseResult = new QueryParser().parse(request.getQuery());
        List<String> queryTerms;
        List<String> phraseTerms = null;
        queryTerms = removeStopwords(stem(queryParseResult.getQueryTerms()));
        if (!queryParseResult.getQuotedTerms().isEmpty()) {
            phraseTerms = removeStopwords(stem(queryParseResult.getQuotedTerms()));
        }

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
    
    private List<String> stem(List<String> words) {
        return words.stream()
                .map(stemmer::stem)
                .collect(Collectors.toList());
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

    //TODO: Repository type
    private Set<Long> filterPhraseInTable(List<String> phrase, boolean raw, String table, int phraseSearchDistance, boolean stemForRaw) throws JsonProcessingException {
        Map<Long, List<Set<Integer>>> uidPositionList = new HashMap<>();
        
        for (int idx = 0; idx < phrase.size(); idx++) {
            String word = phrase.get(idx);
            Long wid = wordListRepository.findWidByWord(word);
            
            if (wid == null) {
                return new HashSet<>(); // No URL contains the phrase
            }

            List<String> result;
            if (table.equals("body")) {
                if (raw && stemForRaw) {
                    result = rawInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else if (raw) {
                    result = stemmedRawInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else {
                    result = invertedIndexRepository.getInvertedIndexPosition(wid);
                }
            } else { // table == "title"
                if (raw && stemForRaw) {
                    result = rawTitleInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else if (raw) {
                    result = stemmedRawTitleInvertedIndexRepository.getInvertedIndexPosition(wid);
                } else {
                    result = titleInvertedIndexRepository.getInvertedIndexPosition(wid);
                }
            }
            
            if (result.isEmpty()) {
                return new HashSet<>();
            }
            Map<Long, Set<Integer>> bodyQuery = indexParser.parsePostionsInfo(result.get(0));
            
            if (idx != 0) {
                // Filter URLs that contain all words in the phrase
                uidPositionList.keySet().removeIf(urlId -> !bodyQuery.containsKey(urlId));
            }
            
            for (Map.Entry<Long, Set<Integer>> entry : bodyQuery.entrySet()) {
                Long urlId = entry.getKey();
                Set<Integer> wordPositions = entry.getValue();
                
                if (idx == 0 || (uidPositionList.containsKey(urlId) && 
                        isContainPhrase(uidPositionList.get(urlId).get(idx-1), wordPositions, phraseSearchDistance))) {
                    uidPositionList.computeIfAbsent(urlId, k -> new ArrayList<>()).add(wordPositions);
                } else {
                    uidPositionList.remove(urlId);
                }
            }
        }
        
        return new HashSet<Long>(uidPositionList.keySet());
    }
    
    private Set<Long> filterPhrase(List<String> phrase, boolean matchInTitle, boolean raw, boolean stemForRaw, int phraseSearchDistance) throws JsonProcessingException {
        if (!raw) {
            phrase = stem(phrase);
        }
        
        if (matchInTitle) {
            return filterPhraseInTable(phrase, raw, "title", phraseSearchDistance, stemForRaw);
        } else {
            Set<Long> titleResults = filterPhraseInTable(phrase, raw, "title", phraseSearchDistance, stemForRaw);
            Set<Long> bodyResults = filterPhraseInTable(phrase, raw, "body", phraseSearchDistance, stemForRaw);
            
            Set<Long> combinedResults = new HashSet<>(titleResults);
            combinedResults.addAll(bodyResults);
            return combinedResults;
        }
    }

    //TODO: Repository type
    private Map<Long, SimilarityRetrieval> _cosineSimilarity(List<String> query, String invertedIndexTable, Set<Long> filteredUrl) throws JsonProcessingException {
        Map<Long, SimilarityRetrieval> similarityRetrievals = new HashMap<>(); // urlId -> (score, wordPositions)
        double[] queryVector = new double[query.size()];

        for (int idx = 0; idx < query.size(); idx++) {
            String keyWord = query.get(idx);
            Long wid = wordListRepository.findWidByWord(keyWord);
            if (wid == null) {
                continue;
            }

            // Get the inverted index for the word
            List<String> result;
            if (invertedIndexTable.equals("invertedIndex")) {
                result = invertedIndexRepository.getInvertedIndexFullInfo(wid);
            } else { // titleInvertedIndex
                result = titleInvertedIndexRepository.getInvertedIndexFullInfo(wid);
            }
            if (result.isEmpty()) {
                continue;
            }

            Map<Long, FullIndex> bodyQuery = indexParser.parseFullIndex(result.get(0));

            // Set query vector value
            queryVector[idx] = bodyQuery.isEmpty() ? 0 : bodyQuery.values().iterator().next().idf;

            for (Map.Entry<Long, FullIndex> entry : bodyQuery.entrySet()) {
                Long urlId = entry.getKey();
                
                // Filter out URLs not in the filtered set
                if (filteredUrl != null && !filteredUrl.contains(urlId)) {
                    continue;
                }

                FullIndex values = entry.getValue();

                Double documentWeight = urlListRepository.getDocumentWeight(urlId);

                SimilarityRetrieval similarityRetrieval = similarityRetrievals.computeIfAbsent(urlId, k -> new SimilarityRetrieval());
                similarityRetrieval.setSimilarityScore(
                        similarityRetrieval.getSimilarityScore() + (getTermWeight(values.tfNorm, values.idf) / documentWeight)
                );
                similarityRetrieval.getWordPositions().computeIfAbsent(keyWord, k -> new HashSet<>()).addAll(values.positions);
            }
        }
        
        // Normalize query vector
        double queryLength = 0.0;
        for (double v : queryVector) {
            queryLength += v * v;
        }
        queryLength = Math.sqrt(queryLength);

        // Normalize scores
        for (SimilarityRetrieval similarityRetrieval: similarityRetrievals.values()) {
            double score = similarityRetrieval.getSimilarityScore();
            if (queryLength > 0) {
                score /= queryLength;
            }
            similarityRetrieval.setSimilarityScore(score);
        }
        
        return similarityRetrievals;
    }
    
    private double getTermWeight(double tfNorm, double idf) {
        return tfNorm * idf;
    }
    
    private void populateUrlInfo(SearchResult result, Long urlId) throws JsonProcessingException {
        if (result.getUrl() != null) {
            return; // URL info already populated
        }
        UrlList urlList = urlListRepository.findById(urlId).orElse(null);
        if (urlList == null) {
            return; // URL not found
        }

        result.setUrl(urlList.getUrl());
        result.setTitle(urlList.getTitle());
        result.setLastModified(urlList.getLastModified());
        result.setSize(urlList.getContentLength());
        
        // Get parent and child links
        List<Long> parentIds = parentChildRepository.findParentIdsByChildId(urlId);
        List<Long> childIds = parentChildRepository.findChildIdsByParentId(urlId);
        
        result.setParentLinks(parentIds.stream()
                .map(urlListRepository::findUrlByUid)
                .collect(Collectors.toList()));
        
        result.setChildLinks(childIds.stream()
                .map(urlListRepository::findUrlByUid)
                .collect(Collectors.toList()));
        
        // Get keywords
        String forwardIndexHead = forwardIndexRepository.getForwardIndexHead(urlId).get(0);
        Map<String, Integer> keywords = indexParser.parseForwardIndexHeader((String) forwardIndexHead);
        result.setKeywords(keywords);
    }
    
    private List<SearchResult> _search(List<String> query, List<String> phrase, boolean rawMatchPhrase, 
                                      boolean stemForRaw, boolean matchInTitle, int phraseSearchDistance, 
                                      boolean withPageRank) throws JsonProcessingException {
        Map<Long, SearchResult> results = new HashMap<>();
        
        Set<Long> filteredUrl = null;
        if (phrase != null && !phrase.isEmpty()) {
            filteredUrl = filterPhrase(phrase, matchInTitle, rawMatchPhrase, stemForRaw, phraseSearchDistance);
        }
        
        Map<Long, SimilarityRetrieval> bodyInnerProducts = _cosineSimilarity(query, "invertedIndex", filteredUrl);
        Map<Long, SimilarityRetrieval> titleInnerProducts = _cosineSimilarity(query, "titleInvertedIndex", filteredUrl);

        // Process body results
        for (Map.Entry<Long, SimilarityRetrieval> entry : bodyInnerProducts.entrySet()) {
            Long urlId = entry.getKey();
            SimilarityRetrieval similarityRetrieval = entry.getValue();
            double score = similarityRetrieval.getSimilarityScore() * bodyWeight;
            
            SearchResult result = results.computeIfAbsent(urlId, k -> new SearchResult());
            result.setScore(result.getScore() + score);
            result.setWordPos(new HashMap<>());
            for (Map.Entry<String, Set<Integer>> wordPos : similarityRetrieval.getWordPositions().entrySet()) {
                result.getWordPos().put(wordPos.getKey(), new ArrayList<>(wordPos.getValue()));
            }
            
            // Get URL info
            populateUrlInfo(result, urlId);
        }
        
        // Process title results
        for (Map.Entry<Long, SimilarityRetrieval> entry : titleInnerProducts.entrySet()) {
            Long urlId = entry.getKey();
            SimilarityRetrieval similarityRetrieval = entry.getValue();
            double score = similarityRetrieval.getSimilarityScore() * bodyWeight;

            SearchResult result = results.computeIfAbsent(urlId, k -> new SearchResult());
            result.setScore(result.getScore() + score);
            result.setTitleWordPos(new HashMap<>());
            for (Map.Entry<String, Set<Integer>> wordPos : similarityRetrieval.getWordPositions().entrySet()) {
                result.getTitleWordPos().put(wordPos.getKey(), new ArrayList<>(wordPos.getValue()));
            }

            // Get URL info if not already set
            populateUrlInfo(result, urlId);
        }
        
        // Add page rank score
        if (withPageRank) {
            for (SearchResult result : results.values()) {
                Long urlId = urlListRepository.findUidByUrl(result.getUrl());
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
            Long urlId = urlListRepository.findUidByUrl(result.getUrl());
            if (urlId != null) {
                String body = urlBodyRepository.getUrlBody(urlId).get(0);
                if (result.getWordPos() != null && !result.getWordPos().isEmpty()) {
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

    public long getWordListCount() {
        return wordListRepository.count();
    }
}
