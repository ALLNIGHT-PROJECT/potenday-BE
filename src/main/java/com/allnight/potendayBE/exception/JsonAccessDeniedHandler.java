package com.allnight.potendayBE.exception;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
@RequiredArgsConstructor
@Slf4j
public class JsonAccessDeniedHandler implements AccessDeniedHandler {

    private final ApiResponder apiResponder;

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response,
                       AccessDeniedException accessDeniedException) throws IOException, ServletException {
        log.warn("JsonAccessDeniedHandler - AccessDeniedException : {}", accessDeniedException.getMessage());
        apiResponder.sendError(response, ErrorCode.ACCESS_DENIED, accessDeniedException);
    }
}