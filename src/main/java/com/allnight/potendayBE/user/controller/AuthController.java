package com.allnight.potendayBE.user.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.user.dto.NaverLoginRequest;
import com.allnight.potendayBE.user.dto.NaverLoginResponse;
import com.allnight.potendayBE.user.service.NaverOAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final NaverOAuthService naverOAuthService;

    @PostMapping("/naver/login")
    public ResponseEntity<ApiResponse<?>> loginWithNaver(@RequestBody NaverLoginRequest request){
        NaverLoginResponse response = naverOAuthService.login(request.getCode(), request.getState());
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
