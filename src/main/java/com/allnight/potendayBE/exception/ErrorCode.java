package com.allnight.potendayBE.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    // Spring security 인증 & 인가 실패
    ACCESS_TOKEN_MISSING(HttpStatus.UNAUTHORIZED, "AccessToken이 요청에 포함되어있지 않습니다."),
    ACCESS_DENIED(HttpStatus.FORBIDDEN, "접근권한이 없습니다."),

    // JWT 유효성 검증관련 에러
    EMPTY_TOKEN_ERROR(HttpStatus.BAD_REQUEST, "토큰이 비어있습니다."),
    INVALID_TOKEN_SIGNATURE(HttpStatus.FORBIDDEN, "유효하지 않은 토큰입니다. - jwt 서명검증 실패"),
    MALFORMED_TOKEN_ERROR(HttpStatus.UNAUTHORIZED, "유효하지 않은 토큰입니다. - 잘못된 jwt형식"),
    UNSUPPORTED_TOKEN_ERROR(HttpStatus.UNAUTHORIZED, "유효하지 않은 토큰입니다. - 지원하지 않는 jwt"),
    TOKEN_EXPIRED(HttpStatus.UNAUTHORIZED, "유효하지 않은 토큰입니다. - 만료된 토큰"),
    TOKEN_PARSING_FAILED(HttpStatus.UNAUTHORIZED, "유효하지 않은 토큰입니다. - 파싱실패"),

    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "서버내부 문제가 발생했습니다." );

    private final HttpStatus status;
    private final String message;
}
