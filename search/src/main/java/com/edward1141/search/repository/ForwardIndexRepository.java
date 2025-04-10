package com.edward1141.search.repository;

import com.edward1141.search.entity.ForwardIndex;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface ForwardIndexRepository extends JpaRepository<ForwardIndex, Integer> {
    
    @Query("SELECT fi.count, fi.dataHead FROM ForwardIndex fi WHERE fi.uid = :uid")
    Object[] getForwardIndexHead(@Param("uid") Integer uid);
} 