package com.allnight.potendayBE.dailytodo.domain;

import com.allnight.potendayBE.task.domain.Task;
import jakarta.persistence.*;
import lombok.Getter;

import java.time.LocalDateTime;

@Entity
@Getter
public class DailyTodo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "daily_todo_id")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id")
    private Task task;

    private LocalDateTime targetDate;

    private boolean isChecked;

    private int orderIdx;
}
