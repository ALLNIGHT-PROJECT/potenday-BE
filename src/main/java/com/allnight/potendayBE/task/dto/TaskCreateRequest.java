package com.allnight.potendayBE.task.dto;

import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class TaskCreateRequest {
    private String title;
    private String description;
    private String priority;
    private LocalDateTime dueDate;
    private String reference;
}
