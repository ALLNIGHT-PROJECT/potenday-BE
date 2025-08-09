package com.allnight.potendayBE.dailytodo.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DailyTodoDetail {
    private Long todoId;
    private String title;
    private String description;
    private LocalDateTime dueDate;
    private String priority;
    private String reference;

    private List<DailySubTaskDetail> subTasks;
}
