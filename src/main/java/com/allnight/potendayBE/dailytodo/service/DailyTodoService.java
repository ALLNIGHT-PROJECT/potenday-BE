package com.allnight.potendayBE.dailytodo.service;

import com.allnight.potendayBE.dailytodo.domain.DailySubTask;
import com.allnight.potendayBE.dailytodo.domain.DailyTodo;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDetail;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoDto;
import com.allnight.potendayBE.dailytodo.dto.DailyTodoReorderRequest;
import com.allnight.potendayBE.dailytodo.dto.DailySubTaskDetail;
import com.allnight.potendayBE.dailytodo.repository.DailyTodoRepository;
import com.allnight.potendayBE.exception.CustomException;
import com.allnight.potendayBE.exception.ErrorCode;
import com.allnight.potendayBE.task.domain.Task;
import com.allnight.potendayBE.task.domain.TaskPriority;
import com.allnight.potendayBE.user.domain.User;
import com.allnight.potendayBE.user.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

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

    // 요청 유저의 투두조회
    public List<DailyTodoDto> getUserTodoList(Long userId, LocalDate targetDate){
        User user = userService.findByUserId(userId);
        List<DailyTodo> userTodoList = dailyTodoRepository.findByUserTodoWithSubTasks(user, targetDate);
        return userTodoList.stream()
                .map(this::toDetail)
                .toList();
    }
    // 서브테스크 조회 & 관련집계
    private DailyTodoDto toDetail(DailyTodo d) {
        // 서브테스크 DTO 변환
        List<DailySubTaskDetail> subs = (d.getSubTasks() == null ? List.<DailySubTaskDetail>of() :
                d.getSubTasks().stream().map(st -> {
                    DailySubTaskDetail s = new DailySubTaskDetail();
                    s.setSubTaskId(st.getId());
                    s.setTitle(st.getTitle());
                    s.setEstimatedMin(st.getEstimatedTime());   // 필드명 맞춤
                    s.setChecked(st.isCompleted());
                    return s;
                }).toList()
        );

        // 합계,완료,진척 계산
        int totalMin = subs.stream().mapToInt(DailySubTaskDetail::getEstimatedMin).sum();
        boolean allChecked = !subs.isEmpty() && subs.stream().allMatch(DailySubTaskDetail::isChecked);
        double progress = subs.isEmpty() ? 0.0 :
                (subs.stream().filter(DailySubTaskDetail::isChecked).count() * 100.0) / subs.size();

        DailyTodoDto out = new DailyTodoDto();
        out.setTodoId(d.getId());
        out.setTitle(d.getTitle());
        out.setPriority(d.getPriority().name());
        out.setTotalEstimatedTime(totalMin);           // 합계갱신
        out.setDueDate(d.getDueDate());
        out.setCompleted(allChecked);                  // 모든 서브체크 완료 시 true
        out.setOrderIdx(d.getOrderIdx());
        out.setProgressRate(progress);                 // 달성률 갱신
        out.setSubTasks(subs);
        return out;
    }

    // task를 투두로 등록
    @Transactional
    public DailyTodo registerDailyTodo(Task task, LocalDate targetDate, User user) {
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

        // 해당 Priority 그룹 내 최대 orderIdx + 1
        int nextOrder = dailyTodoRepository.findMaxOrderIdxByPriority(user, task.getPriority(), targetDate) + 1;
        dailyTodo.setOrderIdx(nextOrder);

        // SubTask -> DailySubTask로 매핑
        if (task.getSubTasks() != null) {
            List<DailySubTask> clones = task.getSubTasks().stream()
                    .map(sub -> DailySubTask.builder()
                            .dailyTodo(dailyTodo)
                            .title(sub.getTitle())
                            .estimatedTime(sub.getEstimatedTime())
                            .isCompleted(false)
                            .build()
                    ).toList();
            dailyTodo.setSubTasks(clones);
        }

        return dailyTodoRepository.save(dailyTodo);
    }

//    // 우선순위에 따라 정렬
//    public List<DailyTodo> sortByPriorityAndOrderIdx(List<DailyTodo> todos) {
//        return todos.stream()
//                .sorted(
//                        Comparator.comparing((DailyTodo t) -> t.getPriority().getOrder()) // 우선순위 오름차순 (1,2,3)
//                                .thenComparing(DailyTodo::getOrderIdx)                   // orderIdx 오름차순
//                )
//                .toList();
//    }

    // 우선순위 변경
    @Transactional
    public void reorderTodoList(DailyTodoReorderRequest request, LocalDate targetDate, User user) {
        DailyTodo targetTodo = findById(request.getTodoId());
        int oldOrderIdx = targetTodo.getOrderIdx();
        int newOrderIdx = request.getNewOrderIdx();

        if (oldOrderIdx == newOrderIdx) return;

        // 같은 우선순위 그룹의 다른 항목들 조회
        List<DailyTodo> samePriorityTodos = dailyTodoRepository.findByPriorityOrderByIdx( user, targetTodo.getPriority(), targetDate);

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

        // 대상 투두도 함께 저장되도록 추가
        if (!samePriorityTodos.contains(targetTodo)) {
            samePriorityTodos.add(targetTodo);
        }
        dailyTodoRepository.saveAll(samePriorityTodos);
    }

    public DailyTodoDetail getUserTodo(Long userId, Long todoId, LocalDate targetDate){
        User user = userService.findByUserId(userId);
        DailyTodo dailyTodo = dailyTodoRepository.findByIdWithSubTasks(user, targetDate, todoId)
                .orElseThrow(() -> new CustomException(ErrorCode.TODO_NOT_FOUND));

        // 서브태스크 DTO 변환
        List<DailySubTaskDetail> subs = (dailyTodo.getSubTasks() == null ? List.<DailySubTaskDetail>of() :
                dailyTodo.getSubTasks().stream().map(st -> {
                    DailySubTaskDetail s = new DailySubTaskDetail();
                    s.setSubTaskId(st.getId());
                    s.setTitle(st.getTitle());
                    s.setEstimatedMin(st.getEstimatedTime());
                    s.setChecked(st.isCompleted());
                    return s;
                }).toList()
        );

        return DailyTodoDetail.builder()
                .todoId(dailyTodo.getId())
                .title(dailyTodo.getTitle())
                .priority(dailyTodo.getPriority().name())
                .description(dailyTodo.getDescription())
                .dueDate(dailyTodo.getDueDate())
                .reference(dailyTodo.getReference())
                .subTasks(subs)
                .build();
    }

    @Transactional
    public Long updateUserTodo(Long userId, Long todoId, DailyTodoDetail dailyTodoDetail, LocalDate targetDate) {
        User user = userService.findByUserId(userId);

        DailyTodo dailyTodo = dailyTodoRepository.findByIdWithSubTasks(user, targetDate, todoId)
                .orElseThrow(() -> new CustomException(ErrorCode.TODO_NOT_FOUND));
        // DailyTodo 기본 정보 수정
        if (dailyTodoDetail.getTitle() != null)  dailyTodo.setTitle(dailyTodoDetail.getTitle());
        if (dailyTodoDetail.getDescription() != null) dailyTodo.setDescription(dailyTodoDetail.getDescription());
        if (dailyTodoDetail.getDueDate() != null) dailyTodo.setDueDate(dailyTodoDetail.getDueDate());
        if (dailyTodoDetail.getPriority() != null) dailyTodo.setPriority(TaskPriority.valueOf(dailyTodoDetail.getPriority()));
        if (dailyTodoDetail.getReference() != null) dailyTodo.setReference(dailyTodoDetail.getReference());

        // 요청 subTasks null-safe 처리
        List<DailySubTaskDetail> requestSubTasks = dailyTodoDetail.getSubTasks();
        if (requestSubTasks == null) {
            requestSubTasks = Collections.emptyList();
        }

        // 기존 SubTask Map
        Map<Long, DailySubTask> existingSubs = dailyTodo.getSubTasks().stream()
                .filter(st -> st.getId() != null)
                .collect(Collectors.toMap(DailySubTask::getId, st -> st));

        // 요청 ID 모음 (삭제 판단용)
        Set<Long> requestIds = requestSubTasks.stream()
                .map(DailySubTaskDetail::getSubTaskId)
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());

        // 삭제 처리
        dailyTodo.getSubTasks().removeIf(st -> st.getId() != null && !requestIds.contains(st.getId()));

        // 수정·추가 처리
        for (DailySubTaskDetail subReq : requestSubTasks) {
            if (subReq.getSubTaskId() != null && existingSubs.containsKey(subReq.getSubTaskId())) {
                // 수정
                DailySubTask sub = existingSubs.get(subReq.getSubTaskId());
                sub.setTitle(subReq.getTitle());
                sub.setEstimatedTime(subReq.getEstimatedMin());
                sub.setCompleted(subReq.isChecked());
            } else {
                // 추가
                DailySubTask newSub = DailySubTask.builder()
                        .dailyTodo(dailyTodo)
                        .title(subReq.getTitle())
                        .estimatedTime(subReq.getEstimatedMin())
                        .isCompleted(subReq.isChecked())
                        .build();
                dailyTodo.getSubTasks().add(newSub);
            }
        }

        return dailyTodo.getId();
    }
}
