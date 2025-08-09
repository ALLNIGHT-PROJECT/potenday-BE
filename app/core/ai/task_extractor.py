"""
Task Extractor using HyperClova LLM for multi-agent system
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

from app.core.ai.hyperclova import HyperClovaClient
# JsonValidatorAgent not needed with Structured Outputs


class TaskExtractor:
    """Multi-agent for extracting tasks from unstructured text"""
    
    def __init__(self, api_key: str = None):
        try:
            # Use HCX-007 with thinking for task extraction
            self.ai_client = HyperClovaClient(api_key=api_key, model="HCX-007")
            # Import JsonValidatorAgent for validation
            from app.core.ai.json_validator import JsonValidatorAgent
            self.validator = JsonValidatorAgent(api_key=api_key)
        except Exception as e:
            print(f"Warning: HyperClovaClient initialization failed: {e}")
            self.ai_client = None
            self.validator = None
    
    async def extract_tasks(self, original_text: str, user_profile: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Extract tasks and subtasks from unstructured text with user context
        
        Args:
            original_text: Unstructured text containing task information
            user_profile: User's analyzed profile data (optional)
            
        Returns:
            List of tasks with subtasks
        """
        if not self.ai_client:
            # Fallback response when LLM is not available
            return self._generate_fallback_tasks(original_text, user_profile)
        
        # Get current date for context
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Build user context if profile is provided
        user_context = ""
        if user_profile:
            user_context = f"""
사용자 프로필:
- 이름: {user_profile.get('user_name', '알 수 없음')}
- 역할: {user_profile.get('role', '알 수 없음')}
- 전문 기술: {', '.join(user_profile.get('skills', []))}
- 관심사: {', '.join(user_profile.get('interests', []))}
- 업무 스타일: {user_profile.get('work_style', '일반적')}
- 선호 업무 유형: {', '.join(user_profile.get('preferred_task_types', []))}

사용자의 전문성과 선호도를 고려하여 업무를 추출하고 적절한 세부업무를 생성하세요.
"""
        
        # Use prompt engineering to get structured JSON output
        system_prompt = f"""당신은 업무 추출 전문가입니다. 
주어진 텍스트에서 업무(Task)와 세부업무(SubTask)를 추출하여 아래의 정확한 JSON 형식으로만 응답하세요.

오늘 날짜: {current_date}
{user_context}

반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이 순수 JSON만):
{{
  "tasks": [
    {{
      "title": "업무 제목",
      "description": "업무 상세 설명", 
      "priority": "LOW/MID/HIGH 중 하나",
      "dueDate": "YYYY-MM-DDTHH:mm:ss 형식 또는 null",
      "totalEstimatedTime": 숫자(시간 단위, 예: 1.5),
      "isCompleted": false,
      "subTasks": [
        {{
          "title": "세부 업무 제목",
          "estimatedMin": 숫자(분 단위),
          "isChecked": false
        }}
      ],
      "references": "참고 링크 또는 null"
    }}
  ]
}}

우선순위 판단:
- HIGH: 긴급하거나 오늘/내일 마감인 업무
- MID: 일반적인 중요도의 업무  
- LOW: 여유있거나 참고용 업무

날짜 처리:
- "다음 주": 오늘로부터 7일 후 23:59:59
- "이번 달 말": 이번 달 마지막 날 23:59:59
- "내일": 다음 날 23:59:59
- 날짜가 명시되지 않으면 null

시간 추정:
- totalEstimatedTime: 모든 세부업무 시간을 합쳐서 시간 단위로 (예: 90분 = 1.5)
- estimatedMin: 각 세부업무의 예상 소요시간(분)

참고 링크 처리:
- 텍스트에서 특정 업무와 관련된 URL이 언급되면 해당 업무의 references에 추가
- 예: "프레젠테이션 참고 링크: https://example.com" → 프레젠테이션 업무의 references에 추가
- 각 업무별로 관련된 링크만 매칭 (다른 업무의 링크를 섞지 않음)
- 링크가 없으면 null

규칙:
1. 모든 새 업무는 isCompleted: false, isChecked: false
2. 각 업무마다 3-5개의 구체적인 세부업무 생성
3. 사용자의 전문성과 기술 스택을 고려
4. 현실적인 시간 추정 (15분 ~ 240분)
5. 각 업무에 해당하는 참고 링크를 정확히 매칭
6. 순수 JSON만 응답 (```json 같은 마크다운 코드 블록 없음)"""

        user_message = f"""다음 텍스트에서 업무를 추출해주세요.
중요: 각 업무와 관련된 참고 링크가 있다면 해당 업무의 references에만 포함시키세요.
예) "프레젠테이션 참고: https://A.com" → 프레젠테이션 업무에만 https://A.com 포함
예) "보고서 참고: https://B.com" → 보고서 업무에만 https://B.com 포함

텍스트:
{original_text}"""
        
        try:
            # Call HyperClova with Structured Outputs
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            print(f"Calling HCX-007 with thinking (low effort for faster response)...")
            
            # HCX-007 doesn't support Structured Outputs, will use thinking instead
            response = await self.ai_client.chat_completion(
                messages=messages,
                max_tokens=4096,
                thinking_effort="low"  # Use low effort for faster response
            )
            
            print(f"HyperClova response received: {response is not None}")
            
            if response and response.get("content"):
                print(f"Raw LLM response: {response['content'][:500]}...")
                
                # Use JsonValidatorAgent to ensure valid JSON
                if self.validator:
                    expected_format = """{
  "tasks": [
    {
      "title": "업무 제목",
      "description": "상세 설명",
      "priority": "HIGH",
      "dueDate": "2025-08-11T23:59:59",
      "totalEstimatedTime": 1.5,
      "isCompleted": false,
      "subTasks": [
        {"title": "세부업무", "estimatedMin": 30, "isChecked": false}
      ],
      "references": null
    }
  ]
}"""
                    
                    # Ensure valid JSON through multi-turn refinement
                    success, parsed_json, final_content = await self.validator.ensure_valid_json(
                        response["content"],
                        expected_format,
                        max_attempts=3
                    )
                    
                    if success and parsed_json:
                        # Extract tasks from validated JSON
                        if isinstance(parsed_json, dict) and "tasks" in parsed_json:
                            tasks = parsed_json["tasks"]
                            
                            # Convert to our internal format
                            formatted_tasks = []
                            for task in tasks:
                                formatted_task = {
                                    "title": task.get("title", "제목 없음"),
                                    "description": task.get("description", ""),
                                    "dueDate": task.get("dueDate"),
                                    "priority": task.get("priority", "MID").lower(),
                                    "reference": task.get("references") or "",  # null이면 빈 문자열
                                    "subTasks": [
                                        {
                                            "title": st.get("title", "세부 업무"),
                                            "estimatedMin": st.get("estimatedMin", 30)
                                        }
                                        for st in task.get("subTasks", [])
                                    ]
                                }
                                formatted_tasks.append(formatted_task)
                            
                            if formatted_tasks:
                                print(f"Successfully extracted {len(formatted_tasks)} tasks from LLM")
                                return formatted_tasks
                        else:
                            print(f"Unexpected JSON structure: {list(parsed_json.keys()) if isinstance(parsed_json, dict) else type(parsed_json)}")
                    else:
                        print(f"JSON validation failed after all attempts")
            
            # Fallback if parsing fails
            print("Falling back to basic task generation")
            return self._generate_fallback_tasks(original_text, user_profile)
            
        except Exception as e:
            print(f"Error extracting tasks: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return self._generate_fallback_tasks(original_text, user_profile)
    
    def _parse_task_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract tasks"""
        try:
            # Try direct JSON parsing first
            tasks = json.loads(response)
            if isinstance(tasks, list):
                return self._validate_tasks(tasks)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown if present
        try:
            # Remove markdown code blocks
            clean_response = response.replace('```json', '').replace('```', '').strip()
            
            # Try to find complete JSON objects even if array is incomplete
            import re
            # Look for individual task objects
            task_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            task_matches = re.findall(task_pattern, clean_response)
            
            tasks = []
            for match in task_matches:
                try:
                    task = json.loads(match)
                    if 'title' in task:  # Basic validation
                        tasks.append(task)
                except:
                    continue
            
            if tasks:
                return self._validate_tasks(tasks)
            
            # If no individual tasks found, try to find array
            json_match = re.search(r'\[.*?\]', clean_response, re.DOTALL)
            if json_match:
                try:
                    tasks = json.loads(json_match.group())
                    if isinstance(tasks, list):
                        return self._validate_tasks(tasks)
                except:
                    pass
                    
        except Exception as e:
            print(f"Failed to parse task response: {e}")
        
        return []
    
    def _validate_tasks(self, tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Validate and clean task data"""
        validated_tasks = []
        
        for task in tasks:
            if not isinstance(task, dict):
                continue
            
            validated_task = {
                "title": task.get("title", "제목 없음"),
                "description": task.get("description", ""),
                "dueDate": self._parse_due_date(task.get("dueDate")),
                "priority": self._validate_priority(task.get("priority", "mid")),
                "reference": task.get("reference") or "",  # null이면 빈 문자열
                "subTasks": self._validate_subtasks(task.get("subTasks", []))
            }
            
            validated_tasks.append(validated_task)
        
        return validated_tasks
    
    def _parse_due_date(self, date_str: Any) -> Optional[str]:
        """Parse and validate due date"""
        if not date_str or date_str == "null":
            return None
        
        if isinstance(date_str, str):
            # Check if it's already in correct format
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_str
            except:
                pass
            
            # Try to parse various date formats
            # Add more formats as needed
            return None
        
        return None
    
    def _validate_priority(self, priority: str) -> str:
        """Validate and normalize priority"""
        priority = str(priority).lower()
        
        # Map variations to standard values
        priority_map = {
            "urgent": "urgent",
            "high": "high",
            "mid": "mid",
            "medium": "mid",
            "low": "low",
            "normal": "mid"
        }
        
        return priority_map.get(priority, "mid")
    
    def _validate_subtasks(self, subtasks: Any) -> List[Dict[str, Any]]:
        """Validate and clean subtasks"""
        if not isinstance(subtasks, list):
            return []
        
        validated_subtasks = []
        for subtask in subtasks:
            if not isinstance(subtask, dict):
                continue
            
            validated_subtask = {
                "title": subtask.get("title", "세부 업무"),
                "estimatedMin": self._parse_estimated_time(subtask.get("estimatedMin", 30))
            }
            validated_subtasks.append(validated_subtask)
        
        return validated_subtasks
    
    def _parse_estimated_time(self, time_value: Any) -> int:
        """Parse estimated time to minutes"""
        if isinstance(time_value, (int, float)):
            return int(time_value)
        
        if isinstance(time_value, str):
            # Extract numbers from string
            numbers = re.findall(r'\d+', time_value)
            if numbers:
                return int(numbers[0])
        
        return 30  # Default 30 minutes
    
    def _generate_fallback_tasks(self, original_text: str, user_profile: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate fallback tasks when LLM is unavailable"""
        # Simple keyword-based extraction
        lines = original_text.split('\n')
        title = lines[0][:100] if lines else "새 업무"
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, original_text)
        reference = urls[0] if urls else None
        
        # Estimate priority based on keywords
        priority = "mid"
        if any(word in original_text.lower() for word in ['긴급', '급함', 'urgent', 'asap']):
            priority = "urgent"
        elif any(word in original_text.lower() for word in ['중요', 'important', 'critical']):
            priority = "high"
        
        # Create a basic task
        task = {
            "title": title,
            "description": original_text[:500],
            "dueDate": None,
            "priority": priority,
            "reference": reference or "",  # null이면 빈 문자열
            "subTasks": [
                {
                    "title": "내용 검토",
                    "estimatedMin": 30
                },
                {
                    "title": "작업 수행",
                    "estimatedMin": 60
                },
                {
                    "title": "완료 확인",
                    "estimatedMin": 15
                }
            ]
        }
        
        return [task]
    
    async def analyze_task_complexity(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task complexity and provide insights"""
        if not self.ai_client:
            return {
                "complexity": "medium",
                "totalEstimatedMin": sum(st.get("estimatedMin", 0) for st in task.get("subTasks", [])),
                "recommendedApproach": "단계별로 진행하세요"
            }
        
        prompt = f"""다음 업무의 복잡도를 분석하고 추천 접근법을 제시하세요:
        
제목: {task.get('title')}
설명: {task.get('description')}
세부업무 수: {len(task.get('subTasks', []))}

JSON 형식으로 응답:
{{
    "complexity": "low|medium|high",
    "totalEstimatedMin": 총예상시간(분),
    "recommendedApproach": "추천 접근법",
    "potentialRisks": ["위험요소1", "위험요소2"],
    "dependencies": ["의존성1", "의존성2"]
}}"""
        
        try:
            response = await self.ai_client.extract_tasks(prompt, "")
            # Parse and return analysis
            return json.loads(response)
        except:
            return {
                "complexity": "medium",
                "totalEstimatedMin": sum(st.get("estimatedMin", 0) for st in task.get("subTasks", [])),
                "recommendedApproach": "단계별로 진행하세요"
            }