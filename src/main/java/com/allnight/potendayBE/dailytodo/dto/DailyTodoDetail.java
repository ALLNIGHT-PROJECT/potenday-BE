package com.allnight.potendayBE.dailytodo.dto;

import com.allnight.potendayBE.task.domain.Task;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class DailyTodoDetail {
    private Long id;
    private Long taskId;
    private String title;
    private String priority;
    private int totalEstimatedTime;
    private LocalDateTime dueDate;
    private boolean isCompleted;
    private int orderIdx;
}
