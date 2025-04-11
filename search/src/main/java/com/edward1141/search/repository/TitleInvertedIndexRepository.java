package com.edward1141.search.repository;

import com.edward1141.search.entity.TitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TitleInvertedIndexRepository extends JpaRepository<TitleInvertedIndex, Long> {
    
    @Query(value = "SELECT tii.data FROM TitleInvertedIndex tii WHERE tii.wid = :wid", nativeQuery = true)
    List<String> getInvertedIndexFullInfo(@Param("wid") Long wid);
    
    @Query(value = "SELECT tii.data FROM TitleInvertedIndex tii WHERE tii.wid = :wid", nativeQuery = true)
    List<String> getInvertedIndexPosition(@Param("wid") Long wid);
} 