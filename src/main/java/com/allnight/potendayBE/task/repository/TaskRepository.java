package com.allnight.potendayBE.task.repository;

import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class TaskRepository {
    private final EntityManager em;

    public Task save(Task task){
        if(task.getId()==null){
            em.persist(task);
            return task;
        } else {
            return em.merge(task);
        }
    }

    public void saveAll(List<Task> tasks) {
        for (int i = 0; i < tasks.size(); i++) {
            Task task = tasks.get(i);

            if (task.getId() == null) {
                em.persist(task);
            } else {
                em.merge(task);
            }

            // 성능 최적화를 위해 일정 개수마다 flush/clear
            if (i % 50 == 0) {
                em.flush();
                em.clear();
            }
        }
    }

    public Optional<Task> findOne(Long id){
        return Optional.ofNullable(em.find(Task.class, id));
    }

    public List<Task> findUnregisteredTasksByUser(User user) {
        return em.createQuery(""" 
                SELECT t FROM Task t WHERE t.user = :user 
                AND NOT EXISTS ( SELECT 1 FROM DailyTodo d WHERE d.task = t ) 
                ORDER BY t.createdAt ASC
            """, Task.class)
                .setParameter("user", user)
                .getResultList();
    }
}
