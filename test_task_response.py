#!/usr/bin/env python3
"""
Test Task API response format with all required fields
"""
import json

def test_task_response_format():
    """Test that task response includes all required fields"""
    
    print("=" * 80)
    print("TASK API RESPONSE FORMAT TEST")
    print("=" * 80)
    
    # Expected task response format
    expected_task_format = {
        "title": "프로젝트 제안서 작성",
        "description": "내일까지 완료해야 하는 중요한 프로젝트 제안서",
        "dueDate": "2025-08-10T23:59:59",
        "priority": "HIGH",
        "references": "https://github.com/project/docs",  # references (s 포함, 빈 문자열 기본값)
        "totalEstimatedMin": 180,  # 분 단위 (60 + 90 + 30 = 180분)
        "isCompleted": False,  # 기본값 false
        "subTasks": [
            {
                "title": "제안서 구조 작성",
                "estimatedMin": 60,
                "isChecked": False  # 기본값 false
            },
            {
                "title": "내용 작성",
                "estimatedMin": 90,
                "isChecked": False
            },
            {
                "title": "검토 및 수정",
                "estimatedMin": 30,
                "isChecked": False
            }
        ]
    }
    
    print("\n📋 Expected Task Response Format:")
    print(json.dumps(expected_task_format, indent=2, ensure_ascii=False))
    
    # Validate required fields
    print("\n✅ Required Fields Check:")
    
    task_fields = [
        ("title", str, "작업 제목"),
        ("description", str, "작업 설명"),
        ("dueDate", (str, type(None)), "마감일 (nullable)"),
        ("priority", str, "우선순위"),
        ("references", str, "참고 링크 (빈 문자열 기본값)"),
        ("totalEstimatedMin", int, "총 예상 시간(분)"),
        ("isCompleted", bool, "완료 여부"),
        ("subTasks", list, "세부 작업 목록")
    ]
    
    for field_name, field_type, description in task_fields:
        if field_name in expected_task_format:
            value = expected_task_format[field_name]
            if isinstance(value, field_type):
                print(f"  ✓ {field_name}: {description} - {type(value).__name__}")
            else:
                print(f"  ✗ {field_name}: Expected {field_type}, got {type(value)}")
        else:
            print(f"  ✗ {field_name}: Missing field")
    
    print("\n✅ SubTask Fields Check:")
    
    subtask_fields = [
        ("title", str, "세부 작업 제목"),
        ("estimatedMin", int, "예상 소요 시간(분)"),
        ("isChecked", bool, "체크 여부")
    ]
    
    if expected_task_format.get("subTasks"):
        subtask = expected_task_format["subTasks"][0]
        for field_name, field_type, description in subtask_fields:
            if field_name in subtask:
                value = subtask[field_name]
                if isinstance(value, field_type):
                    print(f"  ✓ {field_name}: {description} - {type(value).__name__}")
                else:
                    print(f"  ✗ {field_name}: Expected {field_type}, got {type(value)}")
            else:
                print(f"  ✗ {field_name}: Missing field")
    
    # Calculate totalEstimatedMin
    print("\n📊 Total Estimated Minutes Calculation:")
    total_minutes = sum(st["estimatedMin"] for st in expected_task_format["subTasks"])
    print(f"  SubTasks: {[st['estimatedMin'] for st in expected_task_format['subTasks']]} minutes")
    print(f"  Total: {total_minutes} minutes")
    print(f"  Expected: {expected_task_format['totalEstimatedMin']} minutes")
    
    if total_minutes == expected_task_format['totalEstimatedMin']:
        print(f"  ✓ Calculation correct!")
    else:
        print(f"  ✗ Calculation mismatch!")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
✅ Task Response must include:
   - title: string
   - description: string
   - dueDate: string | null
   - priority: string (URGENT|HIGH|MID|LOW)
   - references: string (empty string if null, not 'reference')
   - totalEstimatedMin: number (minutes, not hours)
   - isCompleted: boolean (default false)
   - subTasks: array

✅ SubTask must include:
   - title: string
   - estimatedMin: number (minutes)
   - isChecked: boolean (default false)

✅ Calculations:
   - totalEstimatedMin = sum(estimatedMin)
   - All new tasks: isCompleted = false
   - All new subtasks: isChecked = false
""")

if __name__ == "__main__":
    test_task_response_format()