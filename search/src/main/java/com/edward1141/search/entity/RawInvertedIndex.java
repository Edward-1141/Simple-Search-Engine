package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "rawInvertedIndex")
@Data
public class RawInvertedIndex {
    @Id
    private Long wid;
    private Integer count;
    private String data;
} 