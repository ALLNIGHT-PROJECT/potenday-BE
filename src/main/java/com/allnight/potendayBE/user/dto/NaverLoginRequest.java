package com.allnight.potendayBE.user.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class NaverLoginRequest {
    private String code;
    private String state;
}
