package com.allnight.potendayBE.task.repository;

import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.domain.TaskSource;
import jakarta.persistence.EntityManager;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@AllArgsConstructor
public class TaskSrcRepository {
    private final EntityManager em;

    public TaskSource save(TaskSource taskSource){
        if(taskSource.getId()==null){
            em.persist(taskSource);
            return taskSource;
        } else {
            return em.merge(taskSource);
        }
    }
}
