package com.edward1141.search.repository;

import com.edward1141.search.entity.WordList;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public interface WordListRepository extends JpaRepository<WordList, Long> {
    
    @Query(value = "SELECT w.wid FROM WordList w WHERE w.word = :word LIMIT 1", nativeQuery = true)
    Long findWidByWord(@Param("word") String word);
    
    @Query(value = "SELECT w.wid as wid, w.word as word FROM WordList w", nativeQuery = true)
    List<Map<String, Object>> getWordIdDict();
} 