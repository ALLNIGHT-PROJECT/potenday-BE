package com.allnight.potendayBE.dailytodo.domain;

import com.allnight.potendayBE.task.domain.SubTask;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.domain.TaskPriority;
import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Getter
@Setter
public class DailyTodo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "daily_todo_id")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", unique = true, nullable = false)
    private Task task;

    private LocalDate targetDate;

    private int orderIdx;

    @OneToMany(mappedBy = "dailyTodo", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<DailySubTask> subTasks;

    // private boolean isCompleted = false;
    // private double progressRate; // 0.0 ~ 100.0 (%)
    // private int totalEstimatedTime;

    // task 관련 영역
    private String title;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "user_id")
    private User user;
    private LocalDateTime dueDate;
    @Enumerated(EnumType.STRING) private TaskPriority priority;
    private String description;
    private String reference;
}
