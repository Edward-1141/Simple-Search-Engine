package com.edward1141.search.repository;

import com.edward1141.search.entity.ParentChild;
import com.edward1141.search.entity.ParentChildId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ParentChildRepository extends JpaRepository<ParentChild, ParentChildId> {
    
    @Query(value = "SELECT pc.childid FROM ParentChild pc WHERE pc.parentid = :uid", nativeQuery = true)
    List<Long> findChildIdsByParentId(@Param("uid") Long uid);
    
    @Query(value = "SELECT pc.parentid FROM ParentChild pc WHERE pc.childid = :uid", nativeQuery = true)
    List<Long> findParentIdsByChildId(@Param("uid") Long uid);
} 