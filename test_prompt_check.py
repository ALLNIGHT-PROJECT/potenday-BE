#!/usr/bin/env python3
"""
Check the improved prompt for reference matching
"""

def show_improved_prompt():
    """Show the improved prompt"""
    
    print("=" * 80)
    print("IMPROVED PROMPT FOR REFERENCE MATCHING")
    print("=" * 80)
    
    system_prompt = """당신은 업무 추출 전문가입니다. 
주어진 텍스트에서 업무(Task)와 세부업무(SubTask)를 추출하여 아래의 정확한 JSON 형식으로만 응답하세요.

[... 기본 설정 ...]

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
6. 순수 JSON만 응답"""
    
    user_message = """다음 텍스트에서 업무를 추출해주세요.
중요: 각 업무와 관련된 참고 링크가 있다면 해당 업무의 references에만 포함시키세요.
예) "프레젠테이션 참고: https://A.com" → 프레젠테이션 업무에만 https://A.com 포함
예) "보고서 참고: https://B.com" → 보고서 업무에만 https://B.com 포함

텍스트:
오늘 회의에서 다음 주까지 프레젠테이션 자료를 준비하고 보고서를 작성해야 한다고 했습니다. 
프레젠테이션 참고 링크는 다음과 같습니다: https://next-volume.com
보고서 참고 링크는: https://last-vast.com"""
    
    print("\n📋 System Prompt (Key Parts):")
    print("-" * 60)
    print("✅ 참고 링크 처리 규칙 추가:")
    print("  - 특정 업무와 관련된 URL만 해당 업무에 매칭")
    print("  - 각 업무별로 독립적인 references 할당")
    print("  - 링크가 없으면 null")
    
    print("\n📋 User Message:")
    print("-" * 60)
    print(user_message)
    
    print("\n🎯 Expected Output:")
    print("-" * 60)
    
    expected = {
        "tasks": [
            {
                "title": "프레젠테이션 자료 준비",
                "references": "https://next-volume.com",  # ✅ 프레젠테이션 링크
                "subTasks": [...]
            },
            {
                "title": "보고서 작성",
                "references": "https://last-vast.com",  # ✅ 보고서 링크
                "subTasks": [...]
            }
        ]
    }
    
    import json
    print(json.dumps(expected, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("KEY IMPROVEMENTS")
    print("=" * 80)
    print("""
1. ✅ System Prompt: Added explicit reference matching rules
2. ✅ User Message: Added clear examples of link-to-task matching
3. ✅ Rule #5: "각 업무에 해당하는 참고 링크를 정확히 매칭"
4. ✅ Clear separation: Each task gets its own specific reference
""")

if __name__ == "__main__":
    show_improved_prompt()