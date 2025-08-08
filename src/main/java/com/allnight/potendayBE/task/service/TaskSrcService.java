package com.allnight.potendayBE.task.service;

import com.allnight.potendayBE.task.domain.TaskSource;
import com.allnight.potendayBE.task.repository.TaskSrcRepository;
import jakarta.transaction.Transactional;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@AllArgsConstructor
public class TaskSrcService {
    private final TaskSrcRepository taskSrcRepository;

    @Transactional
    public TaskSource saveTaskSource(String rawContent) {
        TaskSource src = new TaskSource();
        src.setRawContent(rawContent);
        src.setCreatedAt(LocalDateTime.now());
        return taskSrcRepository.save(src);
    }
}
