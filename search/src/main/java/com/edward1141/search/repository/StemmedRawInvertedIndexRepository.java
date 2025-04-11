package com.edward1141.search.repository;

import com.edward1141.search.entity.StemmedRawInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StemmedRawInvertedIndexRepository extends JpaRepository<StemmedRawInvertedIndex, Long> {
    
    @Query(value = "SELECT srii.data FROM StemmedRawInvertedIndex srii WHERE srii.wid = :wid LIMIT 1", nativeQuery = true)
    List<String> getInvertedIndexPosition(@Param("wid") Long wid);
} 