package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "rawTitleInvertedIndex")
@Data
public class RawTitleInvertedIndex {
    @Id
    private Integer wid;
    private Integer count;
    private String data;
} 