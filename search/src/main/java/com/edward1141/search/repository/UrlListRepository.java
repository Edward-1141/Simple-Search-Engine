package com.edward1141.search.repository;

import com.edward1141.search.entity.UrlList;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public interface UrlListRepository extends JpaRepository<UrlList, Integer> {
    
    @Query("SELECT u.uid FROM UrlList u WHERE u.url = :url")
    Integer findUidByUrl(@Param("url") String url);
    
    @Query("SELECT u.url FROM UrlList u WHERE u.uid = :uid")
    String findUrlByUid(@Param("uid") Integer uid);
    
    @Query("SELECT u.uid as uid, u.url as url FROM UrlList u")
    List<Map<String, Object>> getUrlIdDict();
    
    @Query("SELECT u.title, u.lastModified, u.contentLength FROM UrlList u WHERE u.uid = :uid")
    Object[] getUrlInfo(@Param("uid") Integer uid);
    
    @Query("SELECT u.documentWeight FROM UrlList u WHERE u.uid = :uid")
    Double getDocumentWeight(@Param("uid") Integer uid);
    
    @Query("SELECT u.titleWeight FROM UrlList u WHERE u.uid = :uid")
    Double getTitleWeight(@Param("uid") Integer uid);
    
    @Query("SELECT u.pageRankScore FROM UrlList u WHERE u.uid = :uid")
    Double getPageRankScore(@Param("uid") Integer uid);
} 