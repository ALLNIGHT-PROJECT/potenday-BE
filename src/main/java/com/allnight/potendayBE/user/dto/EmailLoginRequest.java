package com.allnight.potendayBE.user.dto;

import lombok.Getter;

@Getter
public class EmailLoginRequest {
    private String email;
    private String password;
}