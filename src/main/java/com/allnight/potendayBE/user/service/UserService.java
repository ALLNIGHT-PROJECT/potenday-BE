package com.allnight.potendayBE.user.service;

import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.domain.UserProfile;
import com.allnight.potendayBE.user.dto.UserProfileDto;
import com.allnight.potendayBE.user.repository.UserRepository;
import com.allnight.potendayBE.user.repository.userProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final userProfileRepository userProfileRepository;
    private final RedisTemplate redisTemplate;

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

}
