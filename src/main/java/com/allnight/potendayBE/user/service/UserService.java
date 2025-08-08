package com.allnight.potendayBE.user.service;

import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final RedisTemplate redisTemplate;

    public User findByUserId(Long userId){
        return userRepository.findOne(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }

    public void logout(Long userId) {
        redisTemplate.delete("RT:" + userId);
    }
}
