package com.edward1141.search.repository;

import com.edward1141.search.entity.StemmedRawTitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface StemmedRawTitleInvertedIndexRepository extends JpaRepository<StemmedRawTitleInvertedIndex, Integer> {
    
    @Query("SELECT srtii.count, srtii.data FROM StemmedRawTitleInvertedIndex srtii WHERE srtii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 