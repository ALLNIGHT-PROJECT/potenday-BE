package com.allnight.potendayBE.task.controller;

import com.allnight.potendayBE.common.ApiResponse;
import com.allnight.potendayBE.security.jwt.JwtUtil;
import com.allnight.potendayBE.task.domain.TaskSource;
import com.allnight.potendayBE.task.dto.TaskExtractRequest;
import com.allnight.potendayBE.task.dto.TaskExtractResponse;
import com.allnight.potendayBE.task.service.TaskExtractService;
import com.allnight.potendayBE.task.service.TaskSrcService;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/v1/task")
public class TaskAgentController {
    private final TaskExtractService taskExtractService;
    private final TaskSrcService taskSrcService;
    private final JwtUtil jwtUtil;
    private final UserService userService;

    @PostMapping("/extract")
    public ResponseEntity<ApiResponse<?>> extract(
            @Valid @RequestBody TaskExtractRequest request,
            HttpServletRequest httpServletRequestrequest
    ){
        String token = jwtUtil.resolveToken(httpServletRequestrequest);
        Long userId = jwtUtil.extractUserId(token, false);
        User user = userService.findByUserId(userId);

        // task source저장
        TaskSource taskSource = taskSrcService.saveTaskSource(request.getOriginalText());

        // Idempotency-Key
//        String idemKey = servletRequest.getHeader("Idempotency-Key");
//        if (idemKey == null || idemKey.isBlank()) {
//            idemKey = UUID.randomUUID().toString();
//        }

        // AI 호출, Task 저장
        TaskExtractResponse response = taskExtractService.extractTask(user, taskSource, null);

        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
