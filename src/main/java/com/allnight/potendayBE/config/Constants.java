package com.allnight.potendayBE.config;

import java.util.List;

public class Constants {
    private Constants() {
        throw new AssertionError("Cannot instantiate Constants class");
    }

    // 인증필요없는 URL 리스트
    public static List<String> PERMIT_ALL_URLS = List.of(
            "/api/auth/signup",
            "/api/auth/email-code/send",
            "/api/auth/email-code/verify",
            "/api/auth/login",
            "/api/auth/reissue",
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
