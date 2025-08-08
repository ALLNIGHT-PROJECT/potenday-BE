package com.allnight.potendayBE.task.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AgentTaskExtractRes {
    private Integer cnt;
    private List<TaskItem> tasks;

    @Getter @Setter
    public static class TaskItem {
        private String title;
        private String desc;
        private String priority;
        private String dueDate;
        private String reference;
    }
}
