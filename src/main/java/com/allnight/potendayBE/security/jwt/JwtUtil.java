package com.allnight.potendayBE.security.jwt;

import com.allnight.potendayBE.common.Constants;
import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.security.Key;
import java.util.*;

@Component
@RequiredArgsConstructor
@Slf4j
public class JwtUtil {
    @Value("${jwt.header}")
    private String header;

    @Value("${jwt.access-secret}")
    private String accessSecret;

    @Value("${jwt.refresh-secret}")
    private String refreshSecret;

    @Value("${jwt.access-token-validity-in-seconds}")
    private long accessTokenValidityInSeconds;

    @Value("${jwt.refresh-token-validity-in-seconds}")
    @Getter
    private long refreshTokenValidityInSeconds;

    // 서명키
    private Key accessKey;
    private Key refreshKey;

    @PostConstruct
    public void init() throws Exception {
        if( accessSecret==null || refreshSecret==null ) throw new IllegalStateException("JWT secret이 초기화되지 않았습니다.");

        this.accessKey = Keys.hmacShaKeyFor(Decoders.BASE64.decode(accessSecret));
        this.refreshKey = Keys.hmacShaKeyFor(Decoders.BASE64.decode(refreshSecret));
    }

    // accessToken생성 : 일반요청
    public String createAccessToken(Long userId/*, List<String> authorities*/){
        return Jwts.builder()
                .setSubject(String.valueOf(userId))
                //.claim("authorities", String.join(",", authorities))
                .setExpiration(new Date(System.currentTimeMillis() + accessTokenValidityInSeconds*1000L))
                .signWith(accessKey, SignatureAlgorithm.HS512)
                .compact();
    }

    // refreshToken생성 : 재발급요청
    public String createRefreshToken(Long userId){
        return Jwts.builder()
                .setSubject(String.valueOf(userId))
                .setExpiration(new Date(System.currentTimeMillis() + refreshTokenValidityInSeconds*1000L))
                .signWith(refreshKey, SignatureAlgorithm.HS512)
                .compact();
    }

    // accessToken에서 인증객체 추출
    public Authentication getAuthenticationFromAccessToken(String token){
        // 서명검증후 claim추출
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(accessKey)
                .build()
                .parseClaimsJws(token)
                .getBody();

        /*
        Collection<? extends GrantedAuthority> authorities =
                Arrays.stream(claims.get("authorities").toString().split(","))
                        .map(SimpleGrantedAuthority::new)
                        .collect(Collectors.toList());
         */

        //User principal = new User(claims.getSubject(), "", authorities);
        User principal = new User(claims.getSubject(), "", Collections.emptyList());
        return new UsernamePasswordAuthenticationToken(principal, token, Collections.emptyList());
    }

    // 토큰 유효성 검사
    public boolean validateAccessToken(String token){ return validate(token, accessKey); }
    public boolean validateRefreshToken(String token){ return validate(token, refreshKey); }
    private boolean validate(String token, Key key){
        if (token == null || token.trim().isEmpty()) {
            throw new CustomException(ErrorCode.EMPTY_TOKEN_ERROR);
        }

        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
            return true;
        } catch (SecurityException e){
            log.info("jwt validation 실패 : 서명(signature)검증 실패");
            throw new CustomException(ErrorCode.INVALID_TOKEN_SIGNATURE);
        } catch (MalformedJwtException e){
            log.info("jwt validation 실패 : 잘못된 토큰구조");
            throw new CustomException(ErrorCode.MALFORMED_TOKEN_ERROR);
        } catch (ExpiredJwtException e) {
            log.info("jwt validation 실패 : 만료된 토큰");
            throw new CustomException(ErrorCode.TOKEN_EXPIRED);
        } catch (UnsupportedJwtException e) {
            log.info("jwt validation 실패 : 지원되지 않는 JWT 토큰 형식");
            throw new CustomException(ErrorCode.UNSUPPORTED_TOKEN_ERROR);
        } catch (IllegalArgumentException e) {
            log.warn("jwt validation 실패 : JWT 파싱 실패 - 비어있는 토큰 등");
            throw new CustomException(ErrorCode.TOKEN_PARSING_FAILED);
        }
    }

    // refreshToken 만료 시간 확인
    public Date extractExpiration(String token, boolean isRefresh) {
        Key key = isRefresh ? refreshKey : accessKey;
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getExpiration();
    }

    // 헤더의 token추출
    public String resolveToken(HttpServletRequest request){
        String bearerToken = request.getHeader(Constants.AUTHORIZATION_HEADER);
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    // 토큰에서 식별자 userId 추출
    public Long extractUserId(String token, boolean isRefresh){
        Key key = isRefresh ? refreshKey : accessKey;
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();

        return Long.parseLong(claims.getSubject());
    }
}

