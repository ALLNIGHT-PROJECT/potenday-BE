package com.allnight.potendayBE.user.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
public class NaverLoginResponse {
    private String accessToken;
    private String refreshToken;
    private Long userId;
    private String email;
}
