package com.allnight.potendayBE.task.domain;

import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Getter
@Setter
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "task_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_src_id")
    private TaskSource taskSource;

    private String title;

    private LocalDateTime dueDate;

    @Enumerated(EnumType.STRING)
    private TaskPriority priority;

    private String description;

    private String reference;

    @OneToMany(mappedBy = "task", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SubTask> subTasks;

    private int totalEstimatedTime;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private void recalculateTotalEstimatedTime() {
        this.totalEstimatedTime = subTasks.stream()
                .mapToInt(SubTask::getEstimatedTime) // SubTask의 estimatedTime 필드 합산
                .sum();
    }
}
