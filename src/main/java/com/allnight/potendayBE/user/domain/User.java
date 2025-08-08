package com.allnight.potendayBE.user.domain;

import jakarta.persistence.*;
import lombok.NoArgsConstructor;
import lombok.Getter;
import lombok.Setter;
import lombok.Builder;

import java.time.LocalDateTime;

@Entity
@Getter @Setter
@NoArgsConstructor
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

    @Builder
    public User(LoginProvider provider, String providerId, String userName, String email,
                LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.provider = provider;
        this.providerId = providerId;
        this.userName = userName;
        this.email = email;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}
