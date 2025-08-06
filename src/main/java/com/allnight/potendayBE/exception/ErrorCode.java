package com.allnight.potendayBE.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    // Spring security 인증 & 인가 실패
    ACCESS_TOKEN_MISSING(HttpStatus.UNAUTHORIZED, "AccessToken이 요청에 포함되어있지 않습니다."),
    ACCESS_DENIED(HttpStatus.FORBIDDEN, "접근권한이 없습니다.")
    ;

    private final HttpStatus status;
    private final String message;
}
