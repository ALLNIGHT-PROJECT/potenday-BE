package com.allnight.potendayBE.task.dto;

import com.allnight.potendayBE.task.domain.TaskPriority;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class TaskDetail {
    private Long id;
    private String title;
    private LocalDateTime dueDate;
    private String priority;
    private String reference;
    private int totalEstimatedTime;
}
