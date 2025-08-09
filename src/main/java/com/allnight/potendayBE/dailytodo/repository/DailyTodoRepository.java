package com.allnight.potendayBE.dailytodo.repository;

import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.domain.TaskPriority;
import com.allnight.potendayBE.user.domain.User;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class DailyTodoRepository {

    private final EntityManager em;

    public DailyTodo save(DailyTodo dailyTodo) {
        if(dailyTodo.getId()==null){
            em.persist(dailyTodo);
            return dailyTodo;
        } else {
            return em.merge(dailyTodo);
        }
    }

    public void saveAll(List<DailyTodo> dailyTodos) {
        for (DailyTodo dailyTodo : dailyTodos) {
            if (dailyTodo.getId() == null) {
                em.persist(dailyTodo);
            } else {
                em.merge(dailyTodo);
            }
        }
        em.flush();
    }

    public int findMaxOrderIdxByPriority(User user, TaskPriority priority, LocalDate targetDate) {
        Integer maxOrder = em.createQuery("""
            SELECT MAX(d.orderIdx) FROM DailyTodo d WHERE d.priority = :priority AND d.targetDate = :targetDate
            AND d.user = :user
            """, Integer.class)
                .setParameter("priority", priority)
                .setParameter("targetDate", targetDate)
                .setParameter("user", user)
                .getSingleResult();

        return maxOrder != null ? maxOrder : 0;
    }

    public List<DailyTodo> findByUserTodoWithSubTasks(User user, LocalDate targetDate) {
        return em.createQuery("""
                SELECT DISTINCT d
                FROM DailyTodo d
                LEFT JOIN FETCH d.subTasks s
                WHERE d.user = :user
                  AND d.targetDate = :date
                ORDER BY
                   CASE d.priority
                     WHEN 'HIGH' THEN 1
                     WHEN 'MID'  THEN 2
                     WHEN 'LOW'  THEN 3
                   END,
                   d.orderIdx ASC,
                   s.id ASC
            """, DailyTodo.class)
                .setParameter("user", user)
                .setParameter("date", targetDate)
                .getResultList();
    }

    public Optional<DailyTodo> findOne(Long todoId) {
        return Optional.ofNullable(em.find(DailyTodo.class, todoId));
    }

    public List<DailyTodo> findByPriorityOrderByIdx(TaskPriority priority) {
        return em.createQuery("SELECT d FROM DailyTodo d WHERE d.priority = :priority ORDER BY d.orderIdx ASC", DailyTodo.class)
                .setParameter("priority", priority)
                .getResultList();
    }

    public List<DailyTodo> findByPriorityOrderByIdx(User user, TaskPriority priority, LocalDate targetDate) {
        return em.createQuery("""
            SELECT d FROM DailyTodo d
            WHERE d.priority = :priority
              AND d.user = :user
              AND d.targetDate = :targetDate
            ORDER BY d.orderIdx ASC
        """, DailyTodo.class)
                .setParameter("priority", priority)
                .setParameter("user", user)
                .setParameter("targetDate", targetDate)
                .getResultList();
    }

    public Optional<DailyTodo> findByIdWithSubTasks(User user, LocalDate targetDate, Long todoId) {
        return em.createQuery("""
            SELECT d
            FROM DailyTodo d
            LEFT JOIN FETCH d.subTasks s
            WHERE d.user = :user
              AND d.targetDate = :date
              AND d.id = :todoId
            """, DailyTodo.class)
                .setParameter("user", user)
                .setParameter("date", targetDate)
                .setParameter("todoId", todoId)
                .getResultList().stream().findFirst();
    }
}
