package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "forwardIndex")
@Data
public class ForwardIndex {
    @Id
    private Integer uid;
    private Integer count;
    private String dataHead;
    private String data;
} 