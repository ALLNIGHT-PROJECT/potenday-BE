package com.allnight.potendayBE.task.service;

import com.allnight.potendayBE.config.AgentClient;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.domain.TaskPriority;
import com.allnight.potendayBE.task.domain.TaskSource;
import com.allnight.potendayBE.task.domain.TaskStatus;
import com.allnight.potendayBE.task.dto.AgentTaskExtractReq;
import com.allnight.potendayBE.task.dto.AgentTaskExtractRes;
import com.allnight.potendayBE.task.dto.TaskExtractRequest;
import com.allnight.potendayBE.task.dto.TaskExtractResponse;
import com.allnight.potendayBE.task.repository.TaskRepository;
import com.allnight.potendayBE.user.domain.User;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeParseException;
import java.util.List;

@Service
@RequiredArgsConstructor
public class TaskExtractService {
    private final AgentClient agentClient;
    private final TaskRepository taskRepository;

    @Transactional
    public TaskExtractResponse extractTask(User user, TaskSource taskSource, String idemKey){
        // 에이전트 호출
        AgentTaskExtractReq agentReq = new AgentTaskExtractReq(taskSource.getRawContent(), user.getId());
        AgentTaskExtractRes agentRes = agentClient.extractTasks(agentReq, null);

        // task 리스트 가져오기
        List<AgentTaskExtractRes.TaskItem> items =
                (agentRes != null && agentRes.getTasks() != null) ? agentRes.getTasks() : List.of();

        // 저장
        saveExtractedTask(user, taskSource, items);

        // 응답매핑
        List<TaskExtractResponse.Item> mapped = items.stream()
                .map(t -> new TaskExtractResponse.Item(
                        t.getTitle(),
                        t.getDesc(),
                        t.getDueDate(),
                        t.getPriority(),
                        t.getReference()
                ))
                .toList();
        return new TaskExtractResponse(mapped);
    }

    @Transactional
    protected void saveExtractedTask(User user, TaskSource taskSource,
                                     List<AgentTaskExtractRes.TaskItem> items) {
        if (items == null || items.isEmpty()) return;

        List<Task> entities = items.stream().map(t -> {
            Task task = new Task();
            task.setUser(user);
            task.setTaskSource(taskSource);
            task.setTitle(t.getTitle());
            task.setDescription(t.getDesc());
            task.setReference(t.getReference());
            task.setPriority(TaskPriority.fromString(t.getPriority()));

            // dueDate 변환
            if (t.getDueDate() != null && !t.getDueDate().isBlank()) {
                try {
                    task.setDueDate(LocalDateTime.parse(t.getDueDate()));
                } catch (DateTimeParseException ex) {
                    task.setDueDate(Instant.parse(t.getDueDate())
                            .atZone(ZoneId.systemDefault())
                            .toLocalDateTime());
                }
            }

            task.setCreatedAt(LocalDateTime.now());
            task.setUpdatedAt(LocalDateTime.now());
            return task;
        }).toList();

        taskRepository.saveAll(entities);
    }

}
