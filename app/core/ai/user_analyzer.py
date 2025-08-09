"""
User Profile Analyzer using LangGraph multi-agent system
"""
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from app.core.ai.hyperclova import HyperClovaClient
from app.models.user_analysis import ExperienceLevel


class UserProfileAnalyzer:
    """Multi-agent system for analyzing user profiles"""
    
    def __init__(self, api_key: str = None):
        try:
            self.ai_client = HyperClovaClient(api_key=api_key)
        except Exception as e:
            print(f"Warning: HyperClovaClient initialization failed: {e}")
            self.ai_client = None
        
    async def analyze_user_profile(self, user_name: str, introduction: str) -> str:
        """
        Analyze user profile using LLM
        
        Args:
            user_name: User's name
            introduction: User's self-introduction text
            
        Returns:
            JSON string with user analysis
        """
        if not self.ai_client:
            # Fallback response when LLM is not available
            return json.dumps({
                "user_name": user_name,
                "role": "개발자",
                "department": "개발팀",
                "experience_level": "mid",
                "skills": ["개발", "AI", "생산성"],
                "interests": ["기술", "혁신"],
                "responsibilities": ["소프트웨어 개발"],
                "work_style": "협업적",
                "collaboration_style": "팀워크 중시",
                "personality_traits": ["학습지향", "책임감"],
                "preferred_task_types": ["개발", "문제해결"],
                "keywords_detected": ["AI", "생산성", "개발자"],
                "analysis_confidence": 50
            }, ensure_ascii=False)
        
        system_prompt = f"""당신은 사용자 프로필을 분석하는 전문가입니다.
        
사용자의 이름과 자기소개를 분석하여 다음 형식의 JSON으로 응답해주세요:
{{
    "user_name": "{user_name}",
    "role": "직무/역할 (예: 백엔드 개발자, 프로덕트 매니저)",
    "department": "부서/팀 (예: 개발팀, 기획팀)",
    "experience_level": "junior|mid|senior|lead|executive 중 하나",
    "skills": ["기술1", "기술2", ...],
    "interests": ["관심사1", "관심사2", ...],
    "responsibilities": ["주요 업무1", "주요 업무2", ...],
    "work_style": "업무 스타일 (예: 협업적, 독립적, 체계적)",
    "collaboration_style": "협업 스타일 (예: 팀워크 중시, 자율적)",
    "personality_traits": ["성격 특성1", "성격 특성2", ...],
    "preferred_task_types": ["선호 업무 유형1", ...],
    "keywords_detected": ["핵심 키워드1", "핵심 키워드2", ...],
    "analysis_confidence": 0-100 사이의 신뢰도 점수
}}

중요: 
1. 반드시 순수 JSON 형식으로만 응답하세요.
2. 마크다운 코드 블록(```)을 사용하지 마세요.
3. JSON 앞뒤에 어떤 텍스트도 추가하지 마세요.
4. 오직 유효한 JSON 객체만 반환하세요."""
        
        user_message = f"""다음 사용자의 프로필을 분석해주세요:
이름: {user_name}
자기소개: {introduction}"""
        
        try:
            response = await self.ai_client.extract_tasks(user_message, system_prompt)
            
            # Extract JSON from response
            if response:
                print(f"Raw LLM response: {response}")  # Debug logging
                
                # First try to parse the response directly as JSON
                try:
                    json.loads(response)  # Validate it's valid JSON
                    return response  # Return the raw response if it's valid JSON
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from the response
                    import re
                    # Look for JSON between markdown code blocks (in case LLM still uses them)
                    markdown_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                    if markdown_match:
                        json_str = markdown_match.group(1)
                        try:
                            json.loads(json_str)  # Validate
                            return json_str
                        except json.JSONDecodeError:
                            pass  # Try next method
                    
                    # If not found in markdown, try to find any JSON object
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
                    if json_match:
                        # Validate JSON
                        json_str = json_match.group()
                        try:
                            json.loads(json_str)  # Validate
                            return json_str
                        except json.JSONDecodeError as e:
                            print(f"JSON validation error: {e}")
                            print(f"Attempted to parse: {json_str[:500]}...")  # Show first 500 chars
                            # Return error with partial response
                            return json.dumps({
                                "user_name": user_name,
                                "error": f"JSON parsing error: {str(e)}",
                                "raw_response": response[:500]
                            }, ensure_ascii=False)
                else:
                    # If no valid JSON found, return the raw response for debugging
                    return json.dumps({
                        "user_name": user_name,
                        "raw_response": response[:500],
                        "note": "No JSON found in response"
                    }, ensure_ascii=False)
            
            # Fallback
            return json.dumps({
                "user_name": user_name,
                "error": "분석 실패"
            }, ensure_ascii=False)
            
        except Exception as e:
            print(f"Error analyzing profile: {e}")
            return json.dumps({
                "user_name": user_name,
                "error": str(e)
            }, ensure_ascii=False)
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from user introduction"""
        # Fallback: simple keyword extraction (AI 없이도 작동)
        tech_keywords = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        korean_keywords = re.findall(r'[가-힣]+(?:개발|엔지니어|디자인|매니저|기획|디자이너|마케터)', text)
        
        # 추가 키워드 패턴
        if "AI" in text or "인공지능" in text:
            tech_keywords.append("AI")
        if "생산성" in text:
            korean_keywords.append("생산성")
        if "툴" in text or "tool" in text.lower():
            korean_keywords.append("도구개발")
            
        if self.ai_client:
            prompt = f"""다음 자기소개에서 핵심 키워드를 추출해주세요.
            기술, 도구, 프레임워크, 직무, 관심사 등을 중심으로 추출합니다.
            
            자기소개: {text}
            
            JSON 배열 형식으로만 응답하세요: ["키워드1", "키워드2", ...]"""
            
            try:
                response = await self.ai_client.extract_tasks(text, prompt)
                keywords = json.loads(response) if isinstance(response, str) else response
                if isinstance(keywords, list):
                    return keywords[:10]
            except Exception as e:
                print(f"AI keyword extraction failed: {e}")
        
        return list(set(tech_keywords + korean_keywords))[:10]
    
    async def _analyze_role_and_experience(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze user's role and experience level"""
        prompt = f"""다음 자기소개를 분석하여 사용자의 직무와 경력 수준을 파악해주세요.
        
        자기소개: {text}
        키워드: {', '.join(keywords)}
        
        다음 형식의 JSON으로만 응답하세요:
        {{
            "role": "직무명 (예: 백엔드 개발자, 프로덕트 매니저)",
            "department": "부서/팀 (예: 개발팀, 기획팀)",
            "experience_level": "junior|mid|senior|lead|executive 중 하나",
            "years_of_experience": 추정 경력 연수 (숫자),
            "responsibilities": ["주요 업무1", "주요 업무2"]
        }}"""
        
        try:
            response = await self.ai_client.extract_tasks(text, prompt)
            return json.loads(response) if isinstance(response, str) else response
        except:
            # Fallback analysis
            return {
                "role": self._guess_role_from_keywords(keywords),
                "department": "개발팀",
                "experience_level": "mid",
                "years_of_experience": 3,
                "responsibilities": self._guess_responsibilities(text, keywords)
            }
    
    async def _analyze_skills_and_interests(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze user's skills and interests"""
        prompt = f"""다음 자기소개를 분석하여 사용자의 기술 스택과 관심사를 파악해주세요.
        
        자기소개: {text}
        키워드: {', '.join(keywords)}
        
        다음 형식의 JSON으로만 응답하세요:
        {{
            "skills": ["기술1", "기술2", ...],
            "interests": ["관심사1", "관심사2", ...],
            "learning_topics": ["학습중인 주제1", ...],
            "expertise_areas": ["전문 분야1", ...]
        }}"""
        
        try:
            response = await self.ai_client.extract_tasks(text, prompt)
            return json.loads(response) if isinstance(response, str) else response
        except:
            return {
                "skills": keywords[:5],
                "interests": ["기술 학습", "협업"],
                "learning_topics": [],
                "expertise_areas": []
            }
    
    async def _analyze_personality_and_style(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze user's personality and work style"""
        prompt = f"""다음 자기소개를 분석하여 사용자의 성격과 업무 스타일을 파악해주세요.
        
        자기소개: {text}
        
        다음 형식의 JSON으로만 응답하세요:
        {{
            "work_style": "업무 스타일 (예: 협업적, 독립적, 체계적)",
            "collaboration_style": "협업 스타일 (예: 팀워크 중시, 자율적)",
            "personality_traits": ["성격 특성1", "성격 특성2", ...],
            "preferred_task_types": ["선호 업무 유형1", ...],
            "communication_style": "소통 스타일"
        }}"""
        
        try:
            response = await self.ai_client.extract_tasks(text, prompt)
            return json.loads(response) if isinstance(response, str) else response
        except:
            return {
                "work_style": "협업적",
                "collaboration_style": "팀워크 중시",
                "personality_traits": ["책임감", "학습지향", "협업적"],
                "preferred_task_types": ["개발", "문제 해결"],
                "communication_style": "명확하고 체계적"
            }
    
    async def _synthesize_analysis(self, user_name: str, introduction: str, 
                                  keywords: List[str], role_analysis: Dict,
                                  skills_analysis: Dict, personality_analysis: Dict) -> Dict[str, Any]:
        """Synthesize all analyses into final user profile"""
        
        # Combine all analyses
        final_analysis = {
            "user_name": user_name,
            "role": role_analysis.get("role", "미분류"),
            "department": role_analysis.get("department", "미정"),
            "experience_level": self._map_experience_level(role_analysis.get("experience_level", "mid")),
            "skills": skills_analysis.get("skills", []),
            "interests": skills_analysis.get("interests", []),
            "responsibilities": role_analysis.get("responsibilities", []),
            "work_style": personality_analysis.get("work_style", "일반적"),
            "collaboration_style": personality_analysis.get("collaboration_style", "유연함"),
            "personality_traits": personality_analysis.get("personality_traits", []),
            "preferred_task_types": personality_analysis.get("preferred_task_types", []),
            "keywords_detected": keywords,
            "analysis_confidence": self._calculate_confidence(introduction, keywords),
            "raw_analysis": {
                "role_analysis": role_analysis,
                "skills_analysis": skills_analysis,
                "personality_analysis": personality_analysis
            }
        }
        
        return final_analysis
    
    def _map_experience_level(self, level: str) -> str:
        """Map experience level to enum value"""
        mapping = {
            "junior": ExperienceLevel.JUNIOR,
            "mid": ExperienceLevel.MID,
            "senior": ExperienceLevel.SENIOR,
            "lead": ExperienceLevel.LEAD,
            "executive": ExperienceLevel.EXECUTIVE
        }
        return mapping.get(level.lower(), ExperienceLevel.MID)
    
    def _calculate_confidence(self, text: str, keywords: List[str]) -> int:
        """Calculate analysis confidence score"""
        # Base confidence
        confidence = 50
        
        # Add confidence based on text length
        if len(text) > 100:
            confidence += 20
        elif len(text) > 50:
            confidence += 10
        
        # Add confidence based on keywords found
        if len(keywords) > 5:
            confidence += 20
        elif len(keywords) > 2:
            confidence += 10
        
        # Cap at 100
        return min(confidence, 100)
    
    def _guess_role_from_keywords(self, keywords: List[str]) -> str:
        """Guess role from keywords"""
        role_keywords = {
            "개발자": ["React", "Python", "Java", "JavaScript", "개발"],
            "디자이너": ["UI", "UX", "디자인", "Figma", "Sketch"],
            "기획자": ["기획", "PM", "프로덕트", "매니저"],
            "마케터": ["마케팅", "광고", "SNS", "콘텐츠"]
        }
        
        for role, role_kw in role_keywords.items():
            if any(kw in keywords for kw in role_kw):
                return role
        
        return "전문가"
    
    def _guess_responsibilities(self, text: str, keywords: List[str]) -> List[str]:
        """Guess responsibilities from text"""
        responsibilities = []
        
        if "개발" in text or any("develop" in kw.lower() for kw in keywords):
            responsibilities.append("소프트웨어 개발")
        if "디자인" in text:
            responsibilities.append("디자인 작업")
        if "관리" in text or "매니" in text:
            responsibilities.append("프로젝트 관리")
        if "멘토" in text:
            responsibilities.append("팀원 멘토링")
        
        return responsibilities if responsibilities else ["업무 수행"]