package com.allnight.potendayBE.dailytodo.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DailySubTask {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "sub_task_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "daily_todo_id", nullable = false)
    private DailyTodo dailyTodo;

    private String title;

    private boolean isCompleted;

    private int estimatedTime;
}
