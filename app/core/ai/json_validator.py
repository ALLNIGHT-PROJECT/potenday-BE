"""
JSON Validator Agent for multi-agent system
Ensures proper JSON format through iterative refinement
"""
import json
from typing import Dict, Any, Optional, Tuple
import re

from app.core.ai.hyperclova import HyperClovaClient


class JsonValidatorAgent:
    """Agent for validating and refining JSON outputs"""
    
    def __init__(self, api_key: str = None):
        try:
            # Use HCX-005 for Structured Outputs support (fast and reliable)
            self.ai_client = HyperClovaClient(api_key=api_key, model="HCX-005")
        except Exception as e:
            print(f"Warning: HyperClovaClient initialization failed: {e}")
            self.ai_client = None
    
    def validate_json(self, content: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Validate if content is valid JSON
        
        Returns:
            (is_valid, parsed_json, error_message)
        """
        if not content:
            return False, None, "Empty content"
        
        # Clean common issues
        cleaned = self._clean_json_string(content)
        
        try:
            parsed = json.loads(cleaned)
            return True, parsed, None
        except json.JSONDecodeError as e:
            return False, None, str(e)
    
    def _clean_json_string(self, content: str) -> str:
        """Clean common JSON formatting issues"""
        cleaned = content.strip()
        
        # Remove markdown code blocks
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1].strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
        
        # Remove trailing commas before closing braces/brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # Fix common quote issues
        # But be careful not to break valid JSON strings
        
        return cleaned
    
    async def request_json_refinement(
        self, 
        original_content: str, 
        error_message: str,
        expected_format: str
    ) -> str:
        """
        Request AI to fix JSON formatting issues
        
        Args:
            original_content: The malformed JSON content
            error_message: JSON parsing error message
            expected_format: Expected JSON structure example
        
        Returns:
            Refined JSON string
        """
        if not self.ai_client:
            return original_content
        
        system_prompt = """당신은 JSON 형식 검증 및 수정 전문가입니다.
주어진 텍스트를 올바른 JSON 형식으로 수정해주세요.

규칙:
1. 순수 JSON만 응답 (설명이나 마크다운 없음)
2. 문법적으로 올바른 JSON 생성
3. 모든 문자열은 큰따옴표 사용
4. 후행 쉼표 제거
5. 올바른 데이터 타입 사용 (문자열, 숫자, 불린, null)"""

        user_message = f"""다음 JSON을 수정해주세요:

오류 메시지: {error_message}

잘못된 JSON:
{original_content}

올바른 형식 예시:
{expected_format}

위 예시와 같은 구조로 수정된 올바른 JSON만 응답해주세요."""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Use Structured Outputs for reliable JSON generation
            response_format = {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "priority": {"type": "string", "enum": ["LOW", "MID", "HIGH", "URGENT"]},
                                    "dueDate": {"type": ["string", "null"]},
                                    "totalEstimatedTime": {"type": "number"},
                                    "isCompleted": {"type": "boolean"},
                                    "references": {"type": ["string", "null"]},
                                    "subTasks": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "estimatedMin": {"type": "integer"},
                                                "isChecked": {"type": "boolean"}
                                            },
                                            "required": ["title", "estimatedMin", "isChecked"]
                                        }
                                    }
                                },
                                "required": ["title", "priority", "isCompleted", "subTasks"]
                            }
                        }
                    },
                    "required": ["tasks"]
                }
            }
            
            response = await self.ai_client.chat_completion(
                messages=messages,
                max_tokens=4096,  # HCX-005 uses maxTokens
                response_format=response_format  # HCX-005 supports Structured Outputs!
            )
            
            if response and response.get("content"):
                return response["content"]
            
        except Exception as e:
            print(f"Error in JSON refinement: {e}")
        
        return original_content
    
    async def ensure_valid_json(
        self,
        content: str,
        expected_format: str,
        max_attempts: int = 3
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Ensure content is valid JSON through iterative refinement
        
        Args:
            content: Initial content to validate
            expected_format: Expected JSON structure
            max_attempts: Maximum refinement attempts
            
        Returns:
            (success, parsed_json, final_content)
        """
        current_content = content
        
        for attempt in range(max_attempts):
            print(f"JSON validation attempt {attempt + 1}/{max_attempts}")
            
            # Validate current content
            is_valid, parsed_json, error_msg = self.validate_json(current_content)
            
            if is_valid and parsed_json:
                print(f"✅ Valid JSON obtained on attempt {attempt + 1}")
                return True, parsed_json, current_content
            
            print(f"❌ JSON validation failed: {error_msg}")
            
            if attempt < max_attempts - 1:
                # Request refinement
                print("Requesting JSON refinement from AI...")
                current_content = await self.request_json_refinement(
                    current_content,
                    error_msg,
                    expected_format
                )
            
        # Final attempt with basic cleaning
        cleaned = self._clean_json_string(current_content)
        is_valid, parsed_json, _ = self.validate_json(cleaned)
        
        if is_valid and parsed_json:
            print("✅ Valid JSON after final cleaning")
            return True, parsed_json, cleaned
        
        print("❌ Failed to obtain valid JSON after all attempts")
        return False, None, current_content