#!/usr/bin/env python3
"""
Test reference link matching for different tasks
"""
import asyncio
import os
from app.core.ai.task_extractor import TaskExtractor
import json

async def test_reference_matching():
    """Test that references are correctly matched to their respective tasks"""
    
    print("=" * 80)
    print("REFERENCE LINK MATCHING TEST")
    print("=" * 80)
    
    # Set API key
    os.environ["HYPERCLOVA_API_KEY"] = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
    
    # Test cases
    test_cases = [
        {
            "name": "Multiple tasks with different references",
            "input": """오늘 회의에서 다음 주까지 프레젠테이션 자료를 준비하고 보고서를 작성해야 한다고 했습니다. 
프레젠테이션 참고 링크는 다음과 같습니다: https://presentation-example.com
보고서 참고 링크는: https://report-reference.com"""
        },
        {
            "name": "Mixed tasks with some references",
            "input": """긴급: 버그 수정 - 로그인 API 오류
버그 이슈 링크: https://github.com/project/issues/123

다음 주 월요일까지 마케팅 제안서 작성
마케팅 자료: https://marketing-docs.com

이메일 답장하기 (참고 자료 없음)"""
        },
        {
            "name": "Single reference for multiple related tasks",
            "input": """프로젝트 완료를 위해 다음 작업들이 필요합니다:
1. 코드 리뷰
2. 테스트 작성
3. 문서화

모든 작업은 프로젝트 위키를 참고하세요: https://project-wiki.com"""
        }
    ]
    
    # Initialize extractor
    extractor = TaskExtractor()
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test_case['name']}")
        print(f"{'='*60}")
        print(f"\n📝 Input:")
        print(test_case['input'])
        print("-" * 40)
        
        try:
            # Extract tasks
            tasks = await extractor.extract_tasks(test_case['input'])
            
            if tasks:
                print(f"\n✅ Extracted {len(tasks)} task(s)")
                print("\n📋 Tasks with References:")
                
                for i, task in enumerate(tasks, 1):
                    print(f"\n[Task {i}] {task['title']}")
                    print(f"  Priority: {task.get('priority', 'N/A')}")
                    
                    # Check reference
                    reference = task.get('reference', '')
                    if reference:
                        print(f"  ✅ Reference: {reference}")
                    else:
                        print(f"  ℹ️ Reference: (no reference)")
                    
                    # Show subtasks count
                    if task.get('subTasks'):
                        print(f"  Subtasks: {len(task['subTasks'])} items")
                
                # Verify reference matching
                print("\n🔍 Reference Matching Verification:")
                
                # Check if different tasks have different references
                references = [task.get('reference', '') for task in tasks]
                unique_refs = set(ref for ref in references if ref)
                
                if len(unique_refs) > 1:
                    print(f"  ✅ Found {len(unique_refs)} different references")
                    for ref in unique_refs:
                        tasks_with_ref = [t['title'] for t in tasks if t.get('reference') == ref]
                        print(f"    - {ref[:50]}... → {', '.join(tasks_with_ref)}")
                elif len(unique_refs) == 1:
                    print(f"  ℹ️ All tasks share the same reference: {list(unique_refs)[0][:50]}...")
                else:
                    print(f"  ℹ️ No references found in any tasks")
                
            else:
                print("❌ No tasks extracted")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("REFERENCE MATCHING TEST COMPLETE")
    print("=" * 80)
    print("""
Expected behavior:
- Each task should have its own specific reference if mentioned
- "프레젠테이션" task → presentation URL
- "보고서" task → report URL
- "버그 수정" task → GitHub issue URL
- Tasks without mentioned references → empty string
""")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_reference_matching())