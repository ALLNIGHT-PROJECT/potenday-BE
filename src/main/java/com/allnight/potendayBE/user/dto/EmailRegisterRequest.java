package com.allnight.potendayBE.user.dto;

import lombok.Getter;

@Getter
public class EmailRegisterRequest {
    private String email;
    private String password;
}
