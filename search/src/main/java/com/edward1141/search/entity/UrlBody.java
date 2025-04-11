package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "urlBody")
@Data
public class UrlBody {
    @Id
    private Long uid;
    private String body;
} 