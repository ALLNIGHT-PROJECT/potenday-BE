package com.allnight.potendayBE.dailytodo.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDetail;
import com.allnight.potendayBE.dailytodo.service.DailyTodoService;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.service.TaskService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequiredArgsConstructor
@Slf4j
@RequestMapping("/v1/todo")
public class TodoController {

    private final DailyTodoService dailyTodoService;
    private final TaskService taskService;
    private final JwtUtil jwtUtil;

    @GetMapping("/user")
    public ResponseEntity<ApiResponse<?>> getTodoList( HttpServletRequest request ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        List<DailyTodoDetail> userTodoLists = dailyTodoService.getUsersTodo(userId, LocalDate.now());
        return ResponseEntity.ok(ApiResponse.success(userTodoLists));
    }

    @PostMapping("/{taskId}")
    public ResponseEntity<ApiResponse<?>> postTodo( @PathVariable("taskId") Long taskId ){
        Task task = taskService.findById(taskId);
        DailyTodo todo = dailyTodoService.registerDailyTodo(task, LocalDate.now());
        log.info("TASK -> TODO등록 완료({})", todo.getId());
        return ResponseEntity.ok(ApiResponse.success("TASK -> TODO등록 완료"));
    }



}
