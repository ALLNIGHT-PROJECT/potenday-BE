package com.allnight.potendayBE.task.domain;

import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

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

    private TaskPriority priority;

    private String description;

    private String reference;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
