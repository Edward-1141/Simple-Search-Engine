package com.edward1141.search.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Table(name = "parentchild")
@Data
@IdClass(ParentChildId.class)
public class ParentChild {
    @Id
    private Integer parentid;
    
    @Id
    private Integer childid;
} 