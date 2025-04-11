package com.edward1141.search.repository;

import com.edward1141.search.entity.UrlBody;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UrlBodyRepository extends JpaRepository<UrlBody, Long> {
    
    @Query(value = "SELECT ub.body FROM UrlBody ub WHERE ub.uid = :uid LIMIT 1", nativeQuery = true)
    List<String> getUrlBody(@Param("uid") Long uid);
} 