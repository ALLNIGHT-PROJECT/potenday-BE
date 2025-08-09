package com.allnight.potendayBE.dailytodo.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
public class DailyTodoDto {
    private Long todoId;
    private String title;
    private String priority;
    private LocalDateTime dueDate;
    private int totalEstimatedTime;
    @JsonProperty("isCompleted")
    private boolean completed;
    private int orderIdx;
    private double progressRate;

    private List<DailySubTaskDetail> subTasks;
}
