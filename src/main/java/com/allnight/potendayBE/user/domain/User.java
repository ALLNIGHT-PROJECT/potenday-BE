package com.allnight.potendayBE.user.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Getter @Setter
@Table(name = "service_user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long id;

    @Enumerated(EnumType.STRING)
    private LoginProvider provider;

    private String providerId;

    private String userName;

    private String email;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
