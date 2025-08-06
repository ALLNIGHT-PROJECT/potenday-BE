package com.allnight.potendayBE.exception;

import com.allnight.potendayBE.common.ApiResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
@RequiredArgsConstructor
@Slf4j
public class ApiResponder {
    private final ObjectMapper objectMapper;

    public void sendSuccess(HttpServletResponse response, Object data) throws IOException {
        response.setStatus(HttpServletResponse.SC_OK);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        ApiResponse<Object> successResponse = ApiResponse.success(data);
        try {
            response.getWriter().write(objectMapper.writeValueAsString(successResponse));
        } catch (IOException e) {
            throw new RuntimeException("JSON 직렬화 실패", e);
        }
    }

    public void sendError(HttpServletResponse response, ErrorCode errorCode, Throwable cause) throws IOException {
        response.setStatus(errorCode.getStatus().value());
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        ApiResponse<?> errorResponse = ApiResponse.fail(null, errorCode.name(), errorCode.getMessage());
        try {
            response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
        } catch (IOException e) {
            throw new RuntimeException("JSON 직렬화 실패", e);
        }

        // 예외 정보 로그 출력
        if (cause != null) {
            log.error("[ERROR - APIRESPONSER] {} - {}", errorCode.name(), errorCode.getMessage(), cause);
        } else {
            log.error("[ERROR - APIRESPONSER] {} - {}", errorCode.name(), errorCode.getMessage());
        }
    }

}
