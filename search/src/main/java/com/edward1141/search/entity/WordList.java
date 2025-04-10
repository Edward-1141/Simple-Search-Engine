package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "wordList")
@Data
public class WordList {
    @Id
    private Integer wid;
    private String word;
} 