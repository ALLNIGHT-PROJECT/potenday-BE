package com.allnight.potendayBE.config;

import com.allnight.potendayBE.task.dto.AgentTaskExtractReq;
import com.allnight.potendayBE.task.dto.AgentTaskExtractRes;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

@Component
public class AgentClient {
    private final WebClient webClient;
    private final String token;

    public AgentClient(WebClient agentWebClient, @Value("${agent.token}") String token) {
        this.webClient = agentWebClient;
        this.token = token;
    }

    private <T> T post(String path, Object body, String idempotencyKey, Class<T> type) {
        try {
            return webClient.post()
                    .uri(path)
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + token) // 서버-서버용 서비스 토큰
                    .headers(h -> { if (idempotencyKey != null) h.add("Idempotency-Key", idempotencyKey); })
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(type)
                    .block();
        } catch (WebClientResponseException e) {
            throw new RuntimeException("Agent error: %s %s".formatted(e.getStatusCode(), e.getResponseBodyAsString()), e);
        }
    }

    // 1) /v1/tasks/extract
    public AgentTaskExtractRes extractTasks(AgentTaskExtractReq req, String idempotencyKey) {
        return post("/v1/tasks/extract", req, idempotencyKey, AgentTaskExtractRes.class);
    }

    // 2) /v1/subtasks/extract


}
