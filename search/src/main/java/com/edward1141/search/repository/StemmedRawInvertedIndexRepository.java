package com.edward1141.search.repository;

import com.edward1141.search.entity.StemmedRawInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface StemmedRawInvertedIndexRepository extends JpaRepository<StemmedRawInvertedIndex, Integer> {
    
    @Query("SELECT srii.count, srii.data FROM StemmedRawInvertedIndex srii WHERE srii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 