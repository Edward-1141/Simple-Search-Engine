package com.edward1141.search.utils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;

//TODO: fix duplicate

public class IndexParser {

    public static class FullIndex {
        public int tf;
        public int df;
        public double tfNorm;
        public double idf;
        public Set<Integer> positions = new HashSet<>();

        @Override
        public String toString() {
            return String.format("(%d, %d, %f, %f, %s)",
                    tf, df, tfNorm, idf, positions);
        }
    }


    public Map<Long, FullIndex> parseFullIndex(String jsonInput) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();

        // Parse the JSON into a Map of Long keys to Object arrays
        Map<String, Object[]> rawMap = mapper.readValue(
                jsonInput,
                mapper.getTypeFactory().constructMapType(
                        Map.class, String.class, Object[].class
                )
        );

        Map<Long, FullIndex> result = new HashMap<>();

        rawMap.forEach((key, array) -> {
            FullIndex tuple = new FullIndex();
            tuple.tf = ((Number) array[0]).intValue();
            tuple.df = ((Number) array[1]).intValue();
            tuple.tfNorm = ((Number) array[2]).doubleValue();
            tuple.idf = ((Number) array[3]).doubleValue();

            // Convert the array of numbers to Set<Integer>
            for (Integer num: (List<Integer>) array[4]){
                tuple.positions.add(((Number) num).intValue());
            }

            result.put(Long.parseLong(key), tuple);
        });

        return result;
    }

    public Map<Long, Set<Integer>> parsePostionsInfo(String jsonInput) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();

        // Parse the JSON into a Map of Long keys to Object arrays
        Map<String, Object[]> rawMap = mapper.readValue(
                jsonInput,
                mapper.getTypeFactory().constructMapType(
                        Map.class, String.class, Object[].class
                )
        );

        Map<Long, Set<Integer>> result = new HashMap<>();

        // TODO: More error checking
        rawMap.forEach((key, array) -> {
            Set<Integer> positions = new HashSet<Integer>();
            int idx = array.length - 1;

            // Convert the array of numbers to Set<Integer>
            for (Integer num: (List<Integer>) array[idx]){
                positions.add(((Number) num).intValue());
            }

            result.put(Long.parseLong(key), positions);
        });

        return result;
    }

    public Map<String, Integer> parseForwardIndexHeader(String jsonInput) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();

        return mapper.readValue(
                jsonInput,
                mapper.getTypeFactory().constructMapType(
                        Map.class, String.class, Integer.class
                )
        );
    }

    public static void main(String[] args) throws JsonProcessingException {
        // Example of your valid JSON input
        IndexParser invertedIndexParser = new IndexParser();

//        String jsonInput = "{\"35206069257871717\": [2, 4, 0.3333333333333333, 1.3217558399823195, [85, 47]], \"17007053027201517\": " +
//                "[1, 4, 0.038461538461538464, 1.3217558399823195, [232]], \"60585594248379076\": " +
//                "[1, 4, 0.06666666666666667, 1.3217558399823195, [160]], \"4534138179106058\": " +
//                "[1, 4, 0.02564102564102564, 1.3217558399823195, [264]]}";
//
//        Map<Integer, Set<Integer>> dictionary = invertedIndexParser.parsePostionsInfo(jsonInput);

        String forwardInput = "{\"charact\": 39, \"search\": 15, \"titl\": 13, \"movi\": 7, \"match\": 6, \"aka\": 6, \"imdb\": 5, \"tv\": 5, \"episod\": 5, \"studi\": 5}";
        Map<String, Integer> dictionary = invertedIndexParser.parseForwardIndexHeader(forwardInput);

        // Print the result
        dictionary.forEach((k, v) -> System.out.println(k + ": " + v));
    }
}
