package com.allnight.potendayBE.user.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.dto.*;
import com.allnight.potendayBE.user.service.NaverOAuthService;
import com.allnight.potendayBE.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.Map;

@RestController
@RequestMapping("/v1/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final NaverOAuthService naverOAuthService;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;
    private final UserService userService;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/naver/login")
    public ResponseEntity<ApiResponse<?>> loginWithNaver(@RequestBody NaverLoginRequest request){
        NaverLoginResponse response = naverOAuthService.login(request.getCode(), request.getState());
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/reissue/token")
    public ResponseEntity<ApiResponse<?>> reissueToken(@RequestBody ReissueRequest reissueRequest){
        String refreshToken = reissueRequest.getRefreshToken();

        jwtUtil.validateRefreshToken(refreshToken); // 토큰 유효성 확인
        Long userId = jwtUtil.extractUserId(refreshToken, true); // 유저Id 추출

        // 저장된 refreshToken 검증
        String savedRefreshToken = redisTemplate.opsForValue().get("RT:" + userId);
        if( savedRefreshToken==null ){ // 만료되어 삭제된 refreshtoken, 로그아웃한 유저
            log.error("[REISSUE] userId={} - 저장된 refreshToken 없음 - 만료된경우, 로그아웃한 경우", userId);
            throw new CustomException(ErrorCode.REFRESH_TOKEN_EXPIRED); // 클라이언트에 다시 로그인 요청
        }
        if( !savedRefreshToken.equals(refreshToken) ){
            log.error("[REISSUE] userId={} - 저장된 refreshToken과 불일치", userId);
            throw new CustomException(ErrorCode.MISMATCHED_REFRESH_TOKEN); // 불일치
        }

        // 유저를 조회하여 accessToken 생성
        User user = userService.findByUserId(userId);
        String newAccessToken = jwtUtil.createAccessToken(userId);

        // refreshToken 만료 임박시 재발급
        Date expiration = jwtUtil.extractExpiration(refreshToken, true);
        long daysLeft = Duration.between(Instant.now(), expiration.toInstant()).toDays();

        String newRefreshToken = refreshToken;
        if(daysLeft < 3){ // 임박 기준 : 3일 미만
            newRefreshToken = jwtUtil.createRefreshToken(userId);
            log.info("[REISSUE] userId={} - refreshToken 재발급 (만료 {}일 남음)", userId, daysLeft);
            try{
                redisTemplate.opsForValue().set("RT:" + userId, newRefreshToken,
                        Duration.ofSeconds(jwtUtil.getRefreshTokenValidityInSeconds()));
            } catch (Exception e){
                log.error("[REISSUE] userId={} - Redis 저장 실패", userId, e);
                throw new CustomException(ErrorCode.REDIS_SAVE_FAIL);
            }
        }
        return ResponseEntity.ok(ApiResponse.success(new LoginResponse(newAccessToken, newRefreshToken)));
    }

    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<?>> logout(HttpServletRequest request){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);
        userService.logout(userId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    // 로컬 회원가입
    @PostMapping("/register")
    public ResponseEntity<ApiResponse<?>> register(@RequestBody EmailRegisterRequest req) {
        if (userService.existsByEmail(req.getEmail())) {
            throw new CustomException(ErrorCode.DUPLICATED_EMAIL);
        }
        userService.createLocalUser(req.getEmail(), req.getPassword());
        return ResponseEntity.ok(ApiResponse.success(Map.of("message","OK")));
    }

    // 로컬 로그인
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<?>> login(@RequestBody EmailLoginRequest req) {
        User user = userService.findByEmail(req.getEmail())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        if (user.getPassword() == null || !passwordEncoder.matches(req.getPassword(), user.getPassword())) {
            throw new CustomException(ErrorCode.INVALID_CREDENTIALS);
        }

        Long userId = user.getId();
        String accessToken = jwtUtil.createAccessToken(userId);
        String refreshToken = jwtUtil.createRefreshToken(userId);

        try {
            // ★ 재발급 로직과 키 프리픽스 통일: "RT:"
            redisTemplate.opsForValue().set(
                    "RT:" + userId,
                    refreshToken,
                    Duration.ofSeconds(jwtUtil.getRefreshTokenValidityInSeconds())
            );
        } catch (Exception e) {
            log.error("[LOGIN] userId={} - Redis RT 저장 실패", userId, e);
            throw new CustomException(ErrorCode.REDIS_SAVE_FAIL);
        }

        return ResponseEntity.ok(ApiResponse.success(new LoginResponse(accessToken, refreshToken)));
    }

}
