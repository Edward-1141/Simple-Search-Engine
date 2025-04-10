package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "urlList")
@Data
public class UrlList {
    @Id
    private Integer uid;
    private String url;
    private String title;
    private String lastModified;
    private Integer contentLength;
    private Integer numChild;
    private Double documentWeight;
    private Double titleWeight;
    private Double pageRankScore;
} 