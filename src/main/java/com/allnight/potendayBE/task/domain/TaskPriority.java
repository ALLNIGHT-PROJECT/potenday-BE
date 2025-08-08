package com.allnight.potendayBE.task.domain;

public enum TaskPriority {
    HIGH,
    MID,
    LOW;

    public static TaskPriority fromString(String value) {
        if (value == null) return LOW; // 기본값
        return switch (value.trim().toLowerCase()) {
            case "high", "urgent" -> HIGH;
            case "mid", "medium" -> MID;
            default -> LOW;
        };
    }
}
