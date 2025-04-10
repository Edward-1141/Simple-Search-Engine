package com.edward1141.search.repository;

import com.edward1141.search.entity.WordList;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public interface WordListRepository extends JpaRepository<WordList, Integer> {
    
    @Query("SELECT w.wid FROM WordList w WHERE w.word = :word")
    Integer findWidByWord(@Param("word") String word);
    
    @Query("SELECT w.word FROM WordList w WHERE w.wid = :wid")
    String findWordByWid(@Param("wid") Integer wid);
    
    @Query("SELECT w.wid as wid, w.word as word FROM WordList w")
    List<Map<String, Object>> getWordIdDict();
} 