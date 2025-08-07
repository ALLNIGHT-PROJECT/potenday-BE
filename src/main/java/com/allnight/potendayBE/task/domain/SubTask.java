package com.allnight.potendayBE.task.domain;

import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Getter
public class SubTask {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "sub_task_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id")
    private Task task;

    private String title;

    private String estimatedTime;
}
