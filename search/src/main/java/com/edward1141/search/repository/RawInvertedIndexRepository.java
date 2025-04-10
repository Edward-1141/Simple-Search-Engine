package com.edward1141.search.repository;

import com.edward1141.search.entity.RawInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface RawInvertedIndexRepository extends JpaRepository<RawInvertedIndex, Integer> {
    
    @Query("SELECT rii.count, rii.data FROM RawInvertedIndex rii WHERE rii.wid = :wid")
    Object[] getInvertedIndexPosition(@Param("wid") Integer wid);
} 