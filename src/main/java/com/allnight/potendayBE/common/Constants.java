package com.allnight.potendayBE.common;

import java.util.List;

public class Constants {
    private Constants() {
        throw new AssertionError("Cannot instantiate Constants class");
    }

    // 인증필요없는 URL 리스트
    public static List<String> PERMIT_ALL_URLS = List.of(
            "/v1/auth/naver/login",
            "/auth/**",
            "/v1/auth/reissue/token",
            "/h2-console",
            "/h2-console/",
            "/h2-console/**",
            "/favicon.ico",
            "/error",
            "/test",
            "/swagger-ui/**",
            "/v3/api-docs/**",
            "/swagger-resources/**",
            "/webjars/**"
    );

    // jwt 인증헤더
    public static final String AUTHORIZATION_HEADER = "Authorization";
}
