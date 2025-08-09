package com.allnight.potendayBE.user.service;

import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.domain.UserProfile;
import com.allnight.potendayBE.user.dto.UserProfileDto;
import com.allnight.potendayBE.user.repository.UserRepository;
import com.allnight.potendayBE.user.repository.userProfileRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final userProfileRepository userProfileRepository;
    private final RedisTemplate redisTemplate;
    private final PasswordEncoder passwordEncoder;

    public User findByUserId(Long userId){
        return userRepository.findOne(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }

    public void logout(Long userId) {
        redisTemplate.delete("RT:" + userId);
    }

    public void createOrUpdateUserProfile(Long userId, UserProfileDto userProfileDto) {
        User user = findByUserId(userId);
        UserProfile userProfile = userProfileRepository.findByUserId(userId)
                .orElse(new UserProfile());

        userProfile.setUserName(userProfileDto.getUserName());
        userProfile.setIntroduction(userProfile.getIntroduction());

        userProfileRepository.save(userProfile);
    }

    public UserProfile getUserProfile(Long userId) {
        return userProfileRepository.findByUserId(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_PROFILE_NOT_FOUND));
    }

    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }

    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    @Transactional
    public User createLocalUser(String email, String rawPassword) {
        if (userRepository.existsByEmail(email)) {
            throw new CustomException(ErrorCode.DUPLICATED_EMAIL);
        }
        User u = new User();
        u.setEmail(email);
        u.setPassword(passwordEncoder.encode(rawPassword)); // ★ BCrypt
        return userRepository.save(u);
    }
}
