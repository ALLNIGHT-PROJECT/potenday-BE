#!/usr/bin/env python3
"""
Test the multi-agent JSON validation system
"""
import asyncio
import os
import json
from app.core.ai.task_extractor import TaskExtractor

async def test_multiagent_validation():
    """Test task extraction with multi-agent JSON validation"""
    
    # Set API key
    os.environ["HYPERCLOVA_API_KEY"] = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
    
    # Initialize the task extractor
    extractor = TaskExtractor()
    
    # Test cases with varying complexity
    test_cases = [
        {
            "name": "Simple tasks",
            "text": "오늘 회의 준비하기. 내일까지 보고서 작성하기. 이메일 답장하기.",
            "expected_count": 3
        },
        {
            "name": "Complex project task",
            "text": """다음 주 월요일까지 신제품 런칭 준비:
            1. 마케팅 자료 준비 (브로셔, 웹사이트 업데이트)
            2. 프레스 릴리스 작성 및 배포
            3. 소셜 미디어 캠페인 기획
            4. 런칭 이벤트 장소 예약 및 준비
            각 작업은 최소 2-3일 소요 예상""",
            "expected_count": 1  # Could be 1 main task or 4 separate tasks
        },
        {
            "name": "Development tasks",
            "text": """긴급: 버그 수정 - 로그인 API 오류 해결
            중요: 사용자 대시보드 UI 개선
            참고: https://github.com/company/project/issues/123
            다음 스프린트에 배포 예정""",
            "expected_count": 2
        }
    ]
    
    # Test with user profile
    user_profile = {
        "user_name": "김개발",
        "role": "백엔드 개발자",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "interests": ["마이크로서비스", "클라우드", "DevOps"],
        "work_style": "체계적이고 문서화 중시",
        "preferred_task_types": ["개발", "디버깅", "코드 리뷰"]
    }
    
    print("=" * 80)
    print("Testing Multi-Agent JSON Validation System")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n[Test Case: {test_case['name']}]")
        print(f"Input text: {test_case['text'][:100]}...")
        print(f"Expected tasks: ~{test_case['expected_count']}")
        print("-" * 40)
        
        try:
            # Extract tasks with multi-agent validation
            tasks = await extractor.extract_tasks(
                test_case['text'],
                user_profile if "개발" in test_case['name'] else None
            )
            
            if tasks:
                print(f"✅ Successfully extracted {len(tasks)} task(s)")
                for i, task in enumerate(tasks, 1):
                    print(f"\nTask {i}: {task['title']}")
                    print(f"  Priority: {task.get('priority', 'unknown')}")
                    print(f"  Due Date: {task.get('dueDate', 'Not specified')}")
                    if task.get('subTasks'):
                        print(f"  SubTasks ({len(task['subTasks'])}):")
                        for st in task['subTasks'][:3]:  # Show first 3 subtasks
                            print(f"    - {st['title']} ({st.get('estimatedMin', 30)} min)")
                        if len(task['subTasks']) > 3:
                            print(f"    ... and {len(task['subTasks']) - 3} more")
            else:
                print("❌ No tasks extracted")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
    
    print("\n" + "=" * 80)
    print("Multi-Agent Validation Test Complete")
    print("=" * 80)

async def test_json_validator_directly():
    """Test the JSON validator agent directly"""
    from app.core.ai.json_validator import JsonValidatorAgent
    
    print("\n" + "=" * 80)
    print("Testing JSON Validator Agent Directly")
    print("=" * 80)
    
    os.environ["HYPERCLOVA_API_KEY"] = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
    validator = JsonValidatorAgent()
    
    # Test cases with various JSON issues
    test_cases = [
        {
            "name": "Valid JSON",
            "content": '{"tasks": [{"title": "Test", "priority": "HIGH"}]}',
            "should_pass": True
        },
        {
            "name": "JSON with markdown",
            "content": '```json\n{"tasks": [{"title": "Test", "priority": "MID"}]}\n```',
            "should_pass": True
        },
        {
            "name": "JSON with trailing comma",
            "content": '{"tasks": [{"title": "Test", "priority": "LOW"},]}',
            "should_pass": True
        },
        {
            "name": "Malformed JSON",
            "content": '{"tasks": [{"title": "Test" "priority": "HIGH"}]}',
            "should_pass": False
        }
    ]
    
    expected_format = '{"tasks": [{"title": "Example", "priority": "MID"}]}'
    
    for test_case in test_cases:
        print(f"\n[Test: {test_case['name']}]")
        print(f"Content: {test_case['content'][:50]}...")
        
        success, parsed_json, final_content = await validator.ensure_valid_json(
            test_case['content'],
            expected_format,
            max_attempts=2
        )
        
        if success:
            print(f"✅ Validation succeeded")
            print(f"   Parsed: {json.dumps(parsed_json, ensure_ascii=False)[:100]}")
        else:
            print(f"{'⚠️' if not test_case['should_pass'] else '❌'} Validation failed")
            print(f"   Final content: {final_content[:100]}")

if __name__ == "__main__":
    # Run both tests
    asyncio.run(test_multiagent_validation())
    asyncio.run(test_json_validator_directly())