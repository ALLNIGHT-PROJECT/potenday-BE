package com.allnight.potendayBE.user.repository;

import com.allnight.potendayBE.user.domain.UserProfile;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class userProfileRepository {
    private final EntityManager em;

    public UserProfile save(UserProfile userProfile) {
        if(userProfile.getId()==null){
            em.persist(userProfile);
            return userProfile;
        } else {
            return em.merge(userProfile);
        }
    }

    public Optional<UserProfile> findByUserId(Long userId) {
        return em.createQuery("SELECT up FROM UserProfile up WHERE up.user.id = :userId", UserProfile.class)
                .setParameter("userId", userId)
                .getResultStream()
                .findFirst();
    }
}
