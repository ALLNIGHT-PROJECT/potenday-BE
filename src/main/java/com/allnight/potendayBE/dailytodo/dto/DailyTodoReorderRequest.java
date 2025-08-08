package com.allnight.potendayBE.dailytodo.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class DailyTodoReorderRequest {
    private Long todoId;
    private int newOrderIdx;
}
