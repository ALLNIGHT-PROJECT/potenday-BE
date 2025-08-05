package com.allnight.potendayBE.exception;

import com.allnight.potendayBE.common.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(CustomException.class)
    public ResponseEntity<ApiResponse<?>> handleCustomException(CustomException e){
        log.error("[커스텀 예외발생] {}", e.getErrorCode().name());
        return ResponseEntity
                .status(e.getErrorCode().getHttpStatus())
                .body(ApiResponse.fail(null, e.getErrorCode().name(), e.getErrorCode().getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse> handleValidationException(MethodArgumentNotValidException validException) {
        String errorMessage = validException.getBindingResult().getFieldErrors().stream()
                .map(error -> "[field] "+error.getField() + " - " + error.getDefaultMessage())
                .findFirst()
                .orElse("유효성 검증 실패");

        log.error("[Validation] 유효성검사 실패 예외발생", validException);
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.fail(null, "VALIDATION_ERROR", errorMessage));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<?>> handleOther(Exception exception){
        log.error("[전역예외] 처리되지 않은 예외발생", exception);
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.fail(null, "INTERNAL_SERVER_ERROR", "서버 내부 오류"));
    }
}
