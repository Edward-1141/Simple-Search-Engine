package com.edward1141.search.repository;

import com.edward1141.search.entity.InvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface InvertedIndexRepository extends JpaRepository<InvertedIndex, Integer> {
    
    @Query("SELECT ii.count, ii.data FROM InvertedIndex ii WHERE ii.wid = :wid")
    Object[] getInvertedIndexFullInfo(@Param("wid") Integer wid);
    
    @Query("SELECT ii.count, ii.data FROM InvertedIndex ii WHERE ii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 