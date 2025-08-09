package com.allnight.potendayBE.user.repository;

import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class UserRepository {
    private final EntityManager em;

    public User save(User user) {
        if(user.getId()==null){
            em.persist(user);
            return user;
        } else {
            return em.merge(user);  // 실제 반영된 영속 엔티티 반환
        }
    }

    public User findById(Long id) {
        return em.find(User.class, id);
    }

    public Optional<User> findByEmail(String email) {
        return em.createQuery("select u from User u where u.email = :email", User.class)
                .setParameter("email", email)
                .getResultStream()
                .findFirst();
    }

    public Optional<User> findOne(Long id){ return Optional.ofNullable(em.find(User.class, id)); }

    public boolean existsByEmail(String email){
        return em.createQuery("select count(u) from User u where u.email = :email", Long.class)
                .setParameter("email", email)
                .getSingleResult() > 0;
    };


}
