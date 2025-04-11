package com.edward1141.search.repository;

import com.edward1141.search.entity.StemmedRawTitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StemmedRawTitleInvertedIndexRepository extends JpaRepository<StemmedRawTitleInvertedIndex, Long> {
    
    @Query(value = "SELECT srtii.data FROM StemmedRawTitleInvertedIndex srtii WHERE srtii.wid = :wid LIMIT 1", nativeQuery = true)
    List<String> getInvertedIndexPosition(@Param("wid") Long wid);
} 