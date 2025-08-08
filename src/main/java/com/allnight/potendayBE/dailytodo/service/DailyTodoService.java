package com.allnight.potendayBE.dailytodo.service;

import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDetail;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoReorderRequest;
import com.allnight.potendayBE.dailytodo.repository.DailyTodoRepository;
import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DailyTodoService {
    private final DailyTodoRepository dailyTodoRepository;
    private final UserService userService;

    public DailyTodo findById(Long todoId) {
        return dailyTodoRepository.findOne(todoId)
                .orElseThrow(() -> new CustomException(ErrorCode.TODO_NOT_FOUND));
    }

    public List<DailyTodoDetail> getUsersTodo(Long userId, LocalDate targetDate){
        User user = userService.findByUserId(userId);
        List<DailyTodo> userTodoList = dailyTodoRepository.findByUserToday(user, targetDate);
        return sortByPriorityAndOrderIdx(userTodoList)
                .stream()
                .map(todo -> {
                    DailyTodoDetail detail = new DailyTodoDetail();
                    detail.setId(todo.getId());
                    detail.setTaskId(todo.getTask().getId());
                    detail.setTitle(todo.getTask().getTitle());
                    detail.setPriority(todo.getTask().getPriority().name()); // enum -> 문자열
                    detail.setTotalEstimatedTime(todo.getTask().getTotalEstimatedTime());
                    detail.setDueDate(todo.getTask().getDueDate());
                    detail.setCompleted(todo.isCompleted());
                    detail.setOrderIdx(todo.getOrderIdx());
                    return detail;
                }).toList();
    }

    @Transactional
    public DailyTodo registerDailyTodo(Task task, LocalDate targetDate) {
        DailyTodo dailyTodo = new DailyTodo();
        dailyTodo.setTask(task);
        dailyTodo.setTargetDate(targetDate);

        // Task의 필드 중복 저장
        dailyTodo.setTitle(task.getTitle());
        dailyTodo.setUser(task.getUser());
        dailyTodo.setDueDate(task.getDueDate());
        dailyTodo.setPriority(task.getPriority());
        dailyTodo.setDescription(task.getDescription());
        dailyTodo.setReference(task.getReference());
        dailyTodo.setTotalEstimatedTime(task.getTotalEstimatedTime());

        // 해당 Priority 그룹 내 최대 orderIdx + 1
        int nextOrder = dailyTodoRepository.findMaxOrderIdxByPriority(task.getPriority(), targetDate) + 1;
        dailyTodo.setOrderIdx(nextOrder);

        // SubTask 매핑
        if (task.getSubTasks() != null) {
            task.getSubTasks().forEach(sub -> sub.setDailyTodo(dailyTodo));
        }

        return dailyTodoRepository.save(dailyTodo);
    }

    // 우선순위에 따라 정렬
    public List<DailyTodo> sortByPriorityAndOrderIdx(List<DailyTodo> todos) {
        return todos.stream()
                .sorted(
                        Comparator.comparing((DailyTodo t) -> t.getPriority().getOrder()) // 우선순위 오름차순 (1,2,3)
                                .thenComparing(DailyTodo::getOrderIdx)                   // orderIdx 오름차순
                )
                .toList();
    }

    @Transactional
    public void reorderTodoList(DailyTodoReorderRequest request) {
        DailyTodo targetTodo = findById(request.getTodoId());
        int oldOrderIdx = targetTodo.getOrderIdx();
        int newOrderIdx = request.getNewOrderIdx();

        if (oldOrderIdx == newOrderIdx) return;

        // 같은 우선순위 그룹의 다른 항목들 조회
        List<DailyTodo> samePriorityTodos = dailyTodoRepository.findByPriorityOrderByIdx( targetTodo.getPriority());

        // 유효한 orderIdx 범위 계산
        int minOrderIdx = samePriorityTodos.stream()
                .mapToInt(DailyTodo::getOrderIdx)
                .min().orElse(1);
        int maxOrderIdx = samePriorityTodos.stream()
                .mapToInt(DailyTodo::getOrderIdx)
                .max().orElse(1);

        log.info("해당 우선순위 그룹에서 유효한 순서는 {} ~ {}입니다.", minOrderIdx, maxOrderIdx);
        // 범위 검증
        if (newOrderIdx < minOrderIdx || newOrderIdx > maxOrderIdx) {
            throw new CustomException(ErrorCode.INVALID_ORDER_INDEX);
        }

        // orderIdx 재정렬
        if (oldOrderIdx < newOrderIdx) {
            // 아래로 이동: 사이 항목들을 위로 당기기
            samePriorityTodos.stream()
                    .filter(todo -> todo.getOrderIdx() > oldOrderIdx && todo.getOrderIdx() <= newOrderIdx)
                    .forEach(todo -> todo.setOrderIdx(todo.getOrderIdx() - 1));
        } else {
            // 위로 이동: 사이 항목들을 아래로 밀기
            samePriorityTodos.stream()
                    .filter(todo -> todo.getOrderIdx() >= newOrderIdx && todo.getOrderIdx() < oldOrderIdx)
                    .forEach(todo -> todo.setOrderIdx(todo.getOrderIdx() + 1));
        }

        targetTodo.setOrderIdx(newOrderIdx);
        dailyTodoRepository.saveAll(samePriorityTodos);
    }
}
