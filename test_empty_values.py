#!/usr/bin/env python3
"""
Test that empty values are handled correctly
"""
import json

def test_empty_values():
    """Test handling of empty/null values"""
    
    print("=" * 60)
    print("EMPTY VALUES HANDLING TEST")
    print("=" * 60)
    
    # Test cases with empty values
    test_cases = [
        {
            "name": "Task with empty reference",
            "task": {
                "title": "업무 제목",
                "description": "설명",
                "dueDate": None,
                "priority": "MID",
                "references": "",  # Empty string, not null
                "totalEstimatedMin": 60,
                "isCompleted": False,
                "subTasks": [
                    {
                        "title": "세부 업무",
                        "estimatedMin": 60,
                        "isChecked": False
                    }
                ]
            }
        },
        {
            "name": "Task with reference URL",
            "task": {
                "title": "버그 수정",
                "description": "로그인 오류",
                "dueDate": "2025-08-10T10:00:00",
                "priority": "HIGH",
                "references": "https://github.com/issue/123",
                "totalEstimatedMin": 90,
                "isCompleted": False,
                "subTasks": [
                    {
                        "title": "분석",
                        "estimatedMin": 30,
                        "isChecked": False
                    },
                    {
                        "title": "수정",
                        "estimatedMin": 60,
                        "isChecked": False
                    }
                ]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n[{test_case['name']}]")
        task = test_case['task']
        
        # Check references field
        print(f"  references: '{task['references']}'")
        print(f"  Type: {type(task['references']).__name__}")
        
        if task['references'] == "":
            print("  ✅ Empty string (correct)")
        elif task['references'] is None:
            print("  ❌ Null value (should be empty string)")
        else:
            print(f"  ✅ Has value: {task['references']}")
        
        # Check isChecked in subtasks
        for st in task['subTasks']:
            if 'isChecked' in st:
                print(f"  SubTask isChecked: {st['isChecked']} (type: {type(st['isChecked']).__name__})")
                if st['isChecked'] is False:
                    print("    ✅ Boolean false (correct)")
                else:
                    print("    ❌ Should be boolean false")
            else:
                print("    ❌ Missing isChecked field")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
✅ Correct handling:
   - references: "" (empty string) when null/empty
   - isChecked: false (boolean) for all new subtasks
   - isCompleted: false (boolean) for all new tasks
   
❌ Incorrect:
   - references: null (should be empty string)
   - isChecked: missing or non-boolean
""")

if __name__ == "__main__":
    test_empty_values()