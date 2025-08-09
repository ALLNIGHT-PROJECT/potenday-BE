#!/usr/bin/env python3
"""
Final test for HCX-007 with medium effort + HCX-005 validator
"""
import asyncio
import os
from app.core.ai.task_extractor import TaskExtractor
import json

async def test_task_extraction():
    """Test task extraction with the final configuration"""
    
    print("=" * 80)
    print("FINAL TEST: HCX-007 (medium) + HCX-005 (validator)")
    print("=" * 80)
    
    # Set API key
    os.environ["HYPERCLOVA_API_KEY"] = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
    
    # Test input
    test_input = "오늘 회의에서 다음 주까지 프레젠테이션 자료를 준비하고 보고서를 작성해야 한다고 했습니다. 프레젠테이션 참고 링크는 다음과 같습니다: https://presentation-example.com 보고서 참고 링크는: https://report-reference.com"
    
    print(f"\n📝 Input Text:")
    print(test_input)
    print("-" * 40)
    
    # Initialize extractor
    extractor = TaskExtractor()
    
    print("\n🔄 Processing...")
    print("  - Main Agent: HCX-007 with thinking (LOW effort for faster response)")
    print("  - Validator Agent: HCX-005 with Structured Outputs")
    print("-" * 40)
    
    try:
        # Extract tasks
        tasks = await extractor.extract_tasks(test_input)
        
        if tasks:
            print(f"\n✅ Successfully extracted {len(tasks)} task(s)")
            print("\n📋 Extracted Tasks:")
            
            for i, task in enumerate(tasks, 1):
                print(f"\n[Task {i}]")
                print(f"  Title: {task['title']}")
                print(f"  Description: {task.get('description', 'N/A')}")
                print(f"  Priority: {task.get('priority', 'N/A')}")
                print(f"  Due Date: {task.get('dueDate', 'N/A')}")
                print(f"  Reference: {task.get('reference', 'N/A')}")
                
                if task.get('subTasks'):
                    print(f"  SubTasks ({len(task['subTasks'])} items):")
                    for j, st in enumerate(task['subTasks'], 1):
                        print(f"    {j}. {st['title']} ({st.get('estimatedMin', 0)} min)")
            
            # Verify reference matching
            print("\n🔍 Reference Matching Check:")
            for task in tasks:
                if task.get('reference'):
                    print(f"  ✅ {task['title']} → {task['reference']}")
                else:
                    print(f"  ℹ️ {task['title']} → (no reference)")
                    
        else:
            print("❌ No tasks extracted")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("""
Expected behavior:
- HCX-007 generates task JSON with thinking (may have formatting issues)
- HCX-005 validator fixes any JSON formatting issues with Structured Outputs
- Each task gets its specific reference URL
- All fields properly formatted (isChecked: false, totalEstimatedMin, etc.)
""")

if __name__ == "__main__":
    asyncio.run(test_task_extraction())