package com.allnight.potendayBE.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    ACCESS_DENIED(HttpStatus.FORBIDDEN, "접근권한이 없습니다.");

    private final HttpStatus httpStatus;
    private final String message;
}
