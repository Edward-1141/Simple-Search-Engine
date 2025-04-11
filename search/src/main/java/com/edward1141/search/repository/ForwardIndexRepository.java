package com.edward1141.search.repository;

import com.edward1141.search.entity.ForwardIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ForwardIndexRepository extends JpaRepository<ForwardIndex, Long> {
    
    @Query(value = "SELECT fi.data_head FROM ForwardIndex fi WHERE fi.uid = :uid LIMIT 1", nativeQuery = true)
    List<String> getForwardIndexHead(@Param("uid") Long uid);
} 