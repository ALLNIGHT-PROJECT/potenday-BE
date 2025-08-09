"""
HyperCLOVA X API Integration for Task Management
"""
import httpx
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class HyperClovaClient:
    """
    Client for NAVER HyperCLOVA X API
    Based on CLOVA Studio API v3
    Supports both HCX-005 (fast) and HCX-007 (thinking/structured)
    """
    
    def __init__(self, api_key: str = None, model: str = "HCX-005"):
        self.api_key = api_key or os.getenv("HYPERCLOVA_API_KEY")
        if not self.api_key:
            raise ValueError("HyperCLOVA API key not provided")
        
        # Support both models
        self.model = model
        self.base_url = f"https://clovastudio.stream.ntruss.com/v3/chat-completions/{model}"
        
        # Headers for API v3 requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": f"request-{datetime.now().timestamp()}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,  # Max for both models
        stop_sequences: List[str] = None,
        thinking_effort: str = None,  # Only for HCX-007
        response_format: Dict[str, Any] = None  # Only for HCX-007
    ) -> Dict[str, Any]:
        """
        Send chat completion request to HyperCLOVA X
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            stop_sequences: List of stop sequences
            response_format: JSON Schema for Structured Outputs
            
        Returns:
            API response dictionary
        """
        
        # Convert messages to v3 format
        v3_messages = []
        for msg in messages:
            v3_messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            })
        
        # Prepare request payload based on model
        payload = {
            "messages": v3_messages,
            "includeAiFilters": True,
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 0,
            "repetitionPenalty": 1.1
        }
        
        # Model-specific parameters
        if self.model == "HCX-005":
            # HCX-005 uses maxTokens and supports Structured Outputs
            payload["maxTokens"] = max_tokens
            
            # HCX-005 supports response_format for Structured Outputs
            if response_format:
                payload["response_format"] = response_format
                
        elif self.model == "HCX-007":
            # HCX-007 uses maxCompletionTokens and supports thinking (but not with response_format)
            payload["maxCompletionTokens"] = max_tokens
            
            # Add thinking if specified (incompatible with response_format)
            if thinking_effort:
                payload["thinking"] = {"effort": thinking_effort}
            # Note: HCX-007 cannot use response_format (thinking model limitation)
        
        # Only add stop sequences if provided
        if stop_sequences:
            payload["stop"] = stop_sequences
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60.0  # Increased timeout for thinking models
                )
                
                if response.status_code == 200:
                    # Parse streaming response
                    result = ""
                    for line in response.text.strip().split('\n'):
                        if line.startswith('data:'):
                            data_str = line[5:].strip()
                            if data_str and data_str != '[DONE]':
                                try:
                                    data = json.loads(data_str)
                                    if 'message' in data and 'content' in data['message']:
                                        result += data['message']['content']
                                except json.JSONDecodeError:
                                    continue
                    return {"content": result}
                else:
                    raise Exception(f"HyperCLOVA API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"Error calling HyperCLOVA API: {e}")
            raise
    
    async def extract_tasks(self, text: str, system_prompt: str = None) -> str:
        """
        Extract tasks or analyze text using HyperCLOVA X
        
        Args:
            text: Input text to process
            system_prompt: Custom system prompt (optional)
            
        Returns:
            AI response as string
        """
        
        if system_prompt is None:
            system_prompt = """당신은 텍스트를 분석하는 전문가입니다.
주어진 텍스트를 분석하여 요청에 따라 응답해주세요."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            response = await self.chat_completion(messages)
            
            # Extract content from response
            if response and "content" in response:
                return response["content"]
            
            return ""
            
        except Exception as e:
            print(f"Error calling HyperCLOVA: {e}")
            return ""
    
    async def analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task complexity and dependencies
        
        Args:
            task: Task dictionary to analyze
            
        Returns:
            Analysis results
        """
        
        system_message = """당신은 작업 복잡도와 의존성을 분석하는 전문가입니다.
주어진 작업을 분석하여 다음 정보를 제공해주세요:

JSON 형식으로 응답해주세요:
{
    "complexity": "LOW/MEDIUM/HIGH 중 하나",
    "dependencies": ["의존하는 다른 작업들"],
    "risks": ["잠재적 위험 요소들"],
    "required_skills": ["필요한 기술들"],
    "subtasks": ["하위 작업들 (복잡한 작업인 경우)"]
}"""
        
        user_message = f"다음 작업을 분석해주세요:\n제목: {task.get('title')}\n설명: {task.get('description', '')}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = await self.chat_completion(messages)
            
            if response.get("result") and response["result"].get("message"):
                content = response["result"]["message"]["content"]
                
                try:
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Return default analysis if parsing fails
            return {
                "complexity": "MEDIUM",
                "dependencies": [],
                "risks": [],
                "required_skills": [],
                "subtasks": []
            }
            
        except Exception as e:
            print(f"Error analyzing task: {e}")
            return {
                "complexity": "MEDIUM",
                "dependencies": [],
                "risks": [],
                "required_skills": [],
                "subtasks": []
            }
    
    async def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize tasks based on urgency and importance
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            Prioritized task list
        """
        
        system_message = """당신은 작업 우선순위를 설정하는 전문가입니다.
Eisenhower Matrix와 비즈니스 가치를 고려하여 작업들의 우선순위를 정해주세요.

각 작업에 우선순위를 부여하고, 우선순위가 높은 순서대로 정렬해주세요.
우선순위 레벨: URGENT, HIGH, MEDIUM, LOW"""
        
        task_list = "\n".join([f"- {t.get('title')}: {t.get('description', '')}" for t in tasks])
        user_message = f"다음 작업들의 우선순위를 정해주세요:\n{task_list}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = await self.chat_completion(messages)
            
            # Process response and update task priorities
            if response.get("result") and response["result"].get("message"):
                content = response["result"]["message"]["content"]
                
                # Simple priority assignment based on position
                for i, task in enumerate(tasks):
                    if i < len(tasks) // 4:
                        task["priority"] = "URGENT"
                    elif i < len(tasks) // 2:
                        task["priority"] = "HIGH"
                    elif i < 3 * len(tasks) // 4:
                        task["priority"] = "MEDIUM"
                    else:
                        task["priority"] = "LOW"
            
            return tasks
            
        except Exception as e:
            print(f"Error prioritizing tasks: {e}")
            return tasks


class HyperClovaTaskProcessor:
    """
    Task processor using HyperCLOVA X for multi-step task management
    """
    
    def __init__(self):
        api_key = os.getenv("HYPERCLOVA_API_KEY")
        if api_key:
            self.client = HyperClovaClient(api_key)
        else:
            self.client = None
    
    async def process_workflow(
        self,
        text: str,
        workflow_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Process text through task extraction workflow
        
        Args:
            text: Input text
            workflow_type: Type of workflow (full, extract_only, analyze_only)
            
        Returns:
            Processed results
        """
        
        if not self.client:
            return {
                "success": False,
                "error": "HyperCLOVA API key not configured",
                "tasks": []
            }
        
        try:
            # Step 1: Extract tasks
            tasks = await self.client.extract_tasks(text)
            
            if workflow_type == "extract_only":
                return {
                    "success": True,
                    "tasks": tasks,
                    "extracted_count": len(tasks)
                }
            
            # Step 2: Analyze tasks
            for task in tasks:
                analysis = await self.client.analyze_task(task)
                task["analysis"] = analysis
            
            if workflow_type == "analyze_only":
                return {
                    "success": True,
                    "tasks": tasks,
                    "extracted_count": len(tasks)
                }
            
            # Step 3: Prioritize tasks (full workflow)
            prioritized_tasks = await self.client.prioritize_tasks(tasks)
            
            return {
                "success": True,
                "tasks": prioritized_tasks,
                "extracted_count": len(prioritized_tasks),
                "workflow_completed": "full"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tasks": []
            }