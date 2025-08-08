package com.allnight.potendayBE.user.service;

import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.user.domain.LoginProvider;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.dto.NaverLoginResponse;
import com.allnight.potendayBE.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class NaverOAuthService {

    private final JwtUtil jwtUtil;
    private final WebClient webClient;
    private final UserRepository userRepository;
    private final StringRedisTemplate redisTemplate;

    @Value("${naver.client-id}")
    private String clientId;

    @Value("${naver.client-secret}")
    private String clientSecret;

    @Value("${naver.redirect-uri}")
    private String redirectUri;

    @Value("${naver.token-uri}")
    private String tokenUri;

    @Value("${naver.user-info-uri}")
    private String userInfoUri;

    @Transactional
    public NaverLoginResponse login(String code, String state) {
        // 1. 네이버 토큰 요청
        String token = getAccessTokenFromNaver(code, state);

        // 2. 네이버 유저 정보 요청
        Map<String, Object> userInfo = getUserInfo(token);
        String email = (String) userInfo.get("email");
        String name = (String) userInfo.get("name");
        String naverId = (String) userInfo.get("id");

        // 3. DB에 유저 확인 or 생성
        User user = userRepository.findByEmail(email)
                .orElseGet(() -> userRepository.save(User.builder()
                        .email(email)
                        .userName(name)
                        .providerId(naverId)
                        .provider(LoginProvider.NAVER)
                        .createdAt(LocalDateTime.now())
                        .updatedAt(LocalDateTime.now())
                        .build()));

        // 4. JWT 발급
        // List<String> roles = List.of("ROLE_USER");
        String jwtAccessToken = jwtUtil.createAccessToken(user.getId());
        String jwtRefreshToken = jwtUtil.createRefreshToken(user.getId());

        try {
            // Redis에 refreshToken 저장
            redisTemplate.opsForValue().set("RT:" + user.getId(), jwtRefreshToken, Duration.ofDays(14));
        } catch (Exception e) {
            throw new CustomException(ErrorCode.REDIS_SAVE_FAIL);
        }

        return new NaverLoginResponse(jwtAccessToken, jwtRefreshToken,
                user.getId(), user.getEmail());
    }

    private String getAccessTokenFromNaver(String code, String state) {
        return webClient.post()
                .uri(tokenUri)
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_FORM_URLENCODED_VALUE)
                .bodyValue(
                        "grant_type=authorization_code" +
                                "&client_id=" + clientId +
                                "&client_secret=" + clientSecret +
                                "&code=" + code +
                                "&state=" + state +
                                "&redirect_uri=" + redirectUri
                )
                .retrieve()
                .bodyToMono(Map.class)
                .doOnNext(body -> System.out.println("Naver Token Response: " + body))
                .map(response -> (String) response.get("access_token"))
                .block();
    }

    private Map<String, Object> getUserInfo(String accessToken) {
        return webClient.get()
                .uri(userInfoUri)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> (Map<String, Object>) response.get("response"))
                .block();
    }
}
