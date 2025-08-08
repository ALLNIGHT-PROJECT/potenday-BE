package com.allnight.potendayBE.task.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class TaskExtractResponse {
    private List<Item> tasks;

    @Data @NoArgsConstructor @AllArgsConstructor
    public static class Item {
        private String title;
        private String description;
        private String dueDate;
        private String priority;
        private String reference;
    }
}
