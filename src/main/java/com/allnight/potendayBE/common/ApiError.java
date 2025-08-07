package com.allnight.potendayBE.common;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ApiError {
    private final String code;
    private final String message;
}
