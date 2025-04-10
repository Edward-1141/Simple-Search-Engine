package com.edward1141.search.repository;

import com.edward1141.search.entity.UrlBody;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface UrlBodyRepository extends JpaRepository<UrlBody, Integer> {
    
    @Query("SELECT ub.body FROM UrlBody ub WHERE ub.uid = :uid")
    String getUrlBody(@Param("uid") Integer uid);
} 