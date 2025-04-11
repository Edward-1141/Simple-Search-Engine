package com.edward1141.search.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "urlList")
@Data
public class UrlList {
    @Id
    private Long uid;
    private String url;
    private String title;
    @Column(name = "last_modified")
    private String lastModified;
    @Column(name = "content_length")
    private Integer contentLength;
    @Column(name = "num_child")
    private Integer numChild;
    @Column(name = "document_weight")
    private Double documentWeight;
    @Column(name = "title_weight")
    private Double titleWeight;
    @Column(name = "page_rank_score")
    private Double pageRankScore;
} 