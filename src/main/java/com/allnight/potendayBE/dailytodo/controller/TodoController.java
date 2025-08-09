package com.allnight.potendayBE.dailytodo.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDetail;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDto;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoReorderRequest;
import com.allnight.potendayBE.dailytodo.service.DailyTodoService;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.service.TaskService;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequiredArgsConstructor
@Slf4j
@RequestMapping("/v1/todo")
public class TodoController {

    private final DailyTodoService dailyTodoService;
    private final TaskService taskService;
    private final JwtUtil jwtUtil;
    private final UserService userService;

    @GetMapping
    public ResponseEntity<ApiResponse<?>> getTodoList( HttpServletRequest request ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        List<DailyTodoDto> userTodoLists = dailyTodoService.getUserTodoList(userId, LocalDate.now());
        return ResponseEntity.ok(ApiResponse.success(userTodoLists));
    }

    @PostMapping("/{taskId}")
    public ResponseEntity<ApiResponse<?>> postTodo( HttpServletRequest request, @PathVariable("taskId") Long taskId ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);
        User user = userService.findByUserId(userId);

        Task task = taskService.findById(taskId);
        DailyTodo todo = dailyTodoService.registerDailyTodo(task, LocalDate.now(), user);
        log.info("TASK -> TODO등록 완료({})", todo.getId());
        return ResponseEntity.ok(ApiResponse.success("TASK -> TODO등록 완료"));
    }

    @PatchMapping("/reorder")
    public ResponseEntity<ApiResponse<?>> reorderTodo( HttpServletRequest request, @RequestBody DailyTodoReorderRequest reorderRequest ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);
        User user = userService.findByUserId(userId);

        dailyTodoService.reorderTodoList(reorderRequest, LocalDate.now(), user);
        return ResponseEntity.ok(ApiResponse.success("순서변경완료"));
    }

    @GetMapping("/{todoId}")
    public ResponseEntity<ApiResponse<?>> getTodoDetail( HttpServletRequest request, @PathVariable("todoId") Long todoId ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        DailyTodoDetail dailyTodoDetail = dailyTodoService.getUserTodo(userId, todoId, LocalDate.now());
        return ResponseEntity.ok(ApiResponse.success(dailyTodoDetail));
    }

    @PatchMapping("/{todoId}")
    public ResponseEntity<ApiResponse<?>> patchTodo( HttpServletRequest request,
                                                     @PathVariable("todoId") Long todoId, @RequestBody DailyTodoDetail dailyTodoDetail ){
        String token = jwtUtil.resolveToken(request);
        Long userId = jwtUtil.extractUserId(token, false);

        Long todo = dailyTodoService.updateUserTodo(userId, todoId, dailyTodoDetail, LocalDate.now());
        return ResponseEntity.ok(ApiResponse.success(todo));
    }

//    public ResponseEntity<ApiResponse<?>> checkSubTask( HttpServletRequest request, @RequestBody DailyTodoDetail dailyTodoDetail ){
//        String token = jwtUtil.resolveToken(request);
//        Long userId = jwtUtil.extractUserId(token, false);
//    }


}
