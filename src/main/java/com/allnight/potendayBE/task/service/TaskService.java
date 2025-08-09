package com.allnight.potendayBE.task.service;

import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.dto.TaskDetail;
import com.allnight.potendayBE.task.repository.TaskRepository;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TaskService {
    private final TaskRepository taskRepository;
    private final UserService userService;

    public Task findById(Long taskId){
        return taskRepository.findOne(taskId)
                .orElseThrow(() -> new CustomException(ErrorCode.TASK_NOT_FOUND));
    }

    @Transactional(readOnly = true)
    public List<TaskDetail> getUsersTask(Long userId){
        User user = userService.findByUserId(userId);
        List<Task> unregisteredTasksByUser = taskRepository.findUnregisteredTasksByUser(user);
        return unregisteredTasksByUser.stream()
                .map(task -> {
                    TaskDetail detail = new TaskDetail();
                    detail.setId(task.getId());
                    detail.setTitle(task.getTitle());
                    detail.setDueDate(task.getDueDate());
                    detail.setPriority(task.getPriority().name());
                    detail.setReference(task.getReference());
                    detail.setTotalEstimatedTime(task.getTotalEstimatedTime());
                    return detail;
                }).toList();
    }

}
