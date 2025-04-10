package com.edward1141.search.repository;

import com.edward1141.search.entity.RawTitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface RawTitleInvertedIndexRepository extends JpaRepository<RawTitleInvertedIndex, Integer> {
    
    @Query("SELECT rtii.count, rtii.data FROM RawTitleInvertedIndex rtii WHERE rtii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 