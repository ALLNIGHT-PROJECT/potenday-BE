package com.allnight.potendayBE.common;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class ApiResponse<T> {
    private boolean isSuccess;
    private T data;
    private ApiError error; // 성공시 null

    public static<T> ApiResponse<T> success(T data){
        return ApiResponse.<T>builder()
                .isSuccess(true)
                .data(data)
                .error(null)
                .build();
    }

    public static<T> ApiResponse<T> fail(T data, String code, String message){
        return ApiResponse.<T>builder()
                .isSuccess(false)
                .data(data)
                .error(new ApiError(code, message))
                .build();
    }
}
