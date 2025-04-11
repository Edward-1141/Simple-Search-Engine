package com.edward1141.search.repository;

import com.edward1141.search.entity.UrlList;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public interface UrlListRepository extends JpaRepository<UrlList, Long> {
    
    @Query(value = "SELECT u.uid FROM UrlList u WHERE u.url = :url LIMIT 1", nativeQuery = true)
    Long findUidByUrl(@Param("url") String url);
    
    @Query(value = "SELECT u.url FROM UrlList u WHERE u.uid = :uid LIMIT 1", nativeQuery = true)
    String findUrlByUid(@Param("uid") Long uid);
    
    @Query(value = "SELECT u.title, u.last_modified, u.content_length FROM UrlList u WHERE u.uid = :uid LIMIT 1", nativeQuery = true)
    Object[] getUrlInfo(@Param("uid") Long uid);
    
    @Query(value = "SELECT u.document_weight FROM UrlList u WHERE u.uid = :uid LIMIT 1", nativeQuery = true)
    Double getDocumentWeight(@Param("uid") Long uid);
    
    @Query(value = "SELECT u.title_weight FROM UrlList u WHERE u.uid = :uid LIMIT 1", nativeQuery = true)
    Double getTitleWeight(@Param("uid") Long uid);
    
    @Query(value = "SELECT u.page_rank_score FROM UrlList u WHERE u.uid = :uid LIMIT 1", nativeQuery = true)
    Double getPageRankScore(@Param("uid") Long uid);
} 