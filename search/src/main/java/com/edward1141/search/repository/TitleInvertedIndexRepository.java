package com.edward1141.search.repository;

import com.edward1141.search.entity.TitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface TitleInvertedIndexRepository extends JpaRepository<TitleInvertedIndex, Integer> {
    
    @Query("SELECT tii.count, tii.data FROM TitleInvertedIndex tii WHERE tii.wid = :wid")
    Object[] getInvertedIndexFullInfo(@Param("wid") Integer wid);
    
    @Query("SELECT tii.count, tii.data FROM TitleInvertedIndex tii WHERE tii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 