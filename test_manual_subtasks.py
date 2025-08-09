#!/usr/bin/env python3
"""
Test manual task creation with subTasks
"""
import asyncio
import httpx
import json

async def test_manual_task_with_subtasks():
    """Test manual task creation with subTasks in request"""
    
    print("=" * 80)
    print("TEST: Manual Task Creation with SubTasks")
    print("=" * 80)
    
    # Test configuration
    base_url = "https://223-130-151-253.sslip.io:8443"
    
    # Test data with subTasks
    request_data = {
        "title": "프로젝트 발표 준비",
        "description": "연말 프로젝트 성과 발표를 위한 준비 작업",
        "priority": "HIGH",
        "dueDate": "2025-08-20T17:00:00",
        "reference": "https://project-docs.example.com",
        "subTasks": [
            {"title": "발표 자료 조사하기", "estimatedMin": 90},
            {"title": "슬라이드 디자인 작성", "estimatedMin": 180},
            {"title": "발표 스크립트 준비", "estimatedMin": 60},
            {"title": "리허설 진행하기", "estimatedMin": 45},
            {"title": "최종 검토 및 수정", "estimatedMin": 30}
        ]
    }
    
    print("\n📝 Test Input:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    print("-" * 40)
    
    # Create client with SSL verification disabled
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # First, login to get token
            print("\n🔐 Logging in...")
            login_response = await client.post(
                f"{base_url}/v1/auth/login",
                json={
                    "email": "test@naver.com",
                    "password": "test1234"
                }
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(login_response.text)
                return
            
            login_data = login_response.json()
            token = login_data["data"]["access_token"]
            print(f"✅ Login successful")
            
            # Test manual task creation with subTasks
            print("\n🔄 Creating task with manual subTasks...")
            response = await client.post(
                f"{base_url}/v1/task/manual",
                json=request_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Task created successfully!")
                
                if data.get("success") and data.get("data"):
                    task_data = data["data"]
                    print("\n📋 Created Task:")
                    print(f"  Title: {task_data.get('title')}")
                    print(f"  Description: {task_data.get('description')}")
                    print(f"  Priority: {task_data.get('priority')}")
                    print(f"  Due Date: {task_data.get('dueDate')}")
                    print(f"  Reference: {task_data.get('references')}")
                    print(f"  Total Estimated Min: {task_data.get('totalEstimatedMin')} minutes")
                    print(f"  Is Completed: {task_data.get('isCompleted')}")
                    
                    # Check subtasks
                    if task_data.get('subTasks'):
                        print(f"\n  SubTasks ({len(task_data['subTasks'])} items):")
                        total_calculated = 0
                        for i, st in enumerate(task_data['subTasks'], 1):
                            print(f"    {i}. {st['title']} ({st['estimatedMin']} min) - isChecked: {st['isChecked']}")
                            total_calculated += st['estimatedMin']
                        
                        # Verify calculations
                        print("\n🔍 Verification:")
                        print(f"  ✅ totalEstimatedMin matches: {task_data.get('totalEstimatedMin')} == {total_calculated}")
                        print(f"  ✅ isCompleted is False: {task_data.get('isCompleted') == False}")
                        print(f"  ✅ All isChecked are False: {all(not st['isChecked'] for st in task_data['subTasks'])}")
                        print(f"  ✅ SubTask count matches: {len(task_data['subTasks'])} == {len(request_data['subTasks'])}")
                    else:
                        print("  ❌ No subtasks in response")
                else:
                    print("❌ Unexpected response structure")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Request failed")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("""
Expected behavior:
- Task created with user-provided subTasks (not AI-generated)
- totalEstimatedMin calculated as sum of all subTask estimatedMin values
- isCompleted is False for new task
- isChecked is False for all new subTasks
- All 5 provided subTasks should be created exactly as specified
""")

if __name__ == "__main__":
    asyncio.run(test_manual_task_with_subtasks())