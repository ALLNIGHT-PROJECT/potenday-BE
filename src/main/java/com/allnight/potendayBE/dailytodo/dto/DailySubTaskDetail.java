package com.allnight.potendayBE.dailytodo.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DailySubTaskDetail {
    private Long subTaskId;
    private String title;
    private int estimatedMin;
    @JsonProperty("isChecked")
    private boolean isChecked;
}
