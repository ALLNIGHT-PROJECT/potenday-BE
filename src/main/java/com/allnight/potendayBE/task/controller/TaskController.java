package com.allnight.potendayBE.task.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.task.dto.TaskDetail;
import com.allnight.potendayBE.task.service.TaskService;
import com.allnight.potendayBE.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/v1/task")
public class TaskController {

    private final JwtUtil jwtUtil;
    private final TaskService taskService;
    private final UserService userService;

    @GetMapping
    ResponseEntity<ApiResponse<?>> getUsersTask(HttpServletRequest request){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        List<TaskDetail> userTaskList = taskService.getUsersTask(userId);
        return ResponseEntity.ok(ApiResponse.success(userTaskList));
    }
}
