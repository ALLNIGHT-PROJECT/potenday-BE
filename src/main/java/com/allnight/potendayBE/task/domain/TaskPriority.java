package com.allnight.potendayBE.task.domain;

import lombok.Getter;

public enum TaskPriority {
    HIGH(1),
    MID(2),
    LOW(3);

    @Getter
    private final int order;

    TaskPriority(int order) {
        this.order = order;
    }

    public static TaskPriority fromString(String value) {
        if (value == null) return LOW; // 기본값
        return switch (value.trim().toLowerCase()) {
            case "high", "urgent" -> HIGH;
            case "mid", "medium" -> MID;
            default -> LOW;
        };
    }
}
