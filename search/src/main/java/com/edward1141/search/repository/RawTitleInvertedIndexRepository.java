package com.edward1141.search.repository;

import com.edward1141.search.entity.RawTitleInvertedIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RawTitleInvertedIndexRepository extends JpaRepository<RawTitleInvertedIndex, Long> {
    
    @Query(value = "SELECT rtii.data FROM RawTitleInvertedIndex rtii WHERE rtii.wid = :wid LIMIT 1", nativeQuery = true)
    List<String> getInvertedIndexPosition(@Param("wid") Long wid);
} 