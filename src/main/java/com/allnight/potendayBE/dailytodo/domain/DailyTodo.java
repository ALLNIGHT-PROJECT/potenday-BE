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
    @JoinColumn(name = "task_id")
    private Task task;

    private LocalDate targetDate;

    private boolean isCompleted = false;

    private int orderIdx;

    private double progressRate; // 0.0 ~ 100.0 (%)

    // task 관련 영역
    private String title;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "user_id")
    private User user;
    private LocalDateTime dueDate;
    @Enumerated(EnumType.STRING) private TaskPriority priority;
    private String description;
    private String reference;
    @OneToMany(mappedBy = "dailyTodo", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SubTask> subTasks;
    private int totalEstimatedTime;

    // 달성률 변경
    public void updateProgressRate() {
        if (subTasks == null || subTasks.isEmpty()) {
            this.progressRate = 0.0;
            return;
        }
        long completedCount = subTasks.stream().filter(SubTask::isCompleted).count();
        this.progressRate = (completedCount * 100.0) / subTasks.size();
    }
}
