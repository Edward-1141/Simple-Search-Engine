package com.edward1141.search.repository;

import com.edward1141.search.entity.RawInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RawInvertedIndexRepository extends JpaRepository<RawInvertedIndex, Long> {
    
    @Query(value = "SELECT rii.data FROM RawInvertedIndex rii WHERE rii.wid = :wid LIMIT 1", nativeQuery = true)
    List<String> getInvertedIndexPosition(@Param("wid") Long wid);
} 