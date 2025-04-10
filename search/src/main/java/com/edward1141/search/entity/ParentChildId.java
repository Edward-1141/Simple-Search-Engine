package com.edward1141.search.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ParentChildId implements Serializable {
    private Integer parentid;
    private Integer childid;
} 