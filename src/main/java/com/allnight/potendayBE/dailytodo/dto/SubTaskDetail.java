package com.allnight.potendayBE.dailytodo.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class SubTaskDetail {
    private Long subTaskId;
    private String title;
    private int estimatedMin;
    @JsonProperty("isChecked")
    private boolean isChecked;
}
