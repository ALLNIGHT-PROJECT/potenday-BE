package com.allnight.potendayBE.user.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.user.dto.UserProfileDto;
import com.allnight.potendayBE.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/v1/user")
public class UserController {

    private final UserService userService;
    private final JwtUtil jwtUtil;

    @PostMapping("/profile")
    public ResponseEntity<ApiResponse<?>> postUserProfile(
            HttpServletRequest request, @RequestBody UserProfileDto userProfileDto
    ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        userService.createOrUpdateUserProfile(userId, userProfileDto);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

}
