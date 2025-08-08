package com.allnight.potendayBE.task.domain;

import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class SubTask {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "sub_task_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", nullable = false)
    private Task task;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "daily_todo_id", nullable = true)
    private DailyTodo dailyTodo;

    private String title;

    private boolean isCompleted;

    private int estimatedTime;
}
