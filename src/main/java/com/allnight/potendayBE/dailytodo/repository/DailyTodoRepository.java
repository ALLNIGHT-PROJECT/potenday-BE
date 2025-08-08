package com.allnight.potendayBE.dailytodo.repository;

import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
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

    public int findMaxOrderIdxByPriority(TaskPriority priority, LocalDate targetDate) {
        Integer maxOrder = em.createQuery("""
            SELECT MAX(d.orderIdx)
            FROM DailyTodo d
            WHERE d.priority = :priority
              AND d.targetDate = :targetDate
            """, Integer.class)
                .setParameter("priority", priority)
                .setParameter("targetDate", targetDate)
                .getSingleResult();

        return maxOrder != null ? maxOrder : 0;
    }

    public List<DailyTodo> findByUserToday(User user, LocalDate targetDate) {
        return em.createQuery("select t from DailyTodo t where t.user = :user and t.targetDate = :targetDate" +
                                " order by t.orderIdx asc",
                        DailyTodo.class)
                .setParameter("user", user)
                .setParameter("targetDate", targetDate)
                .getResultList();
    }
}
