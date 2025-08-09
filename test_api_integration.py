#!/usr/bin/env python3
"""
Integration test for the multi-agent task extraction API
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_api_integration():
    """Test the task extraction API with multi-agent validation"""
    
    # API configuration
    base_url = "http://localhost:8000"
    
    # Test data
    test_data = {
        "originalText": """내일까지 중요한 프로젝트 보고서 작성하기
        
        다음 주 월요일 클라이언트 미팅 준비:
        - 프레젠테이션 자료 작성 (2시간)
        - 데모 시스템 준비 (1시간)
        - Q&A 준비 (30분)
        
        긴급: 로그인 버그 수정
        참고 링크: https://github.com/project/issues/123"""
    }
    
    print("=" * 70)
    print("MULTI-AGENT TASK EXTRACTION API TEST")
    print("=" * 70)
    
    print(f"\n📝 Test Input:")
    print("-" * 40)
    print(test_data["originalText"])
    print("-" * 40)
    
    # First, we need to login to get a token
    print("\n🔐 Authenticating...")
    
    async with httpx.AsyncClient() as client:
        # Create test user and login
        try:
            # Try to register first
            register_data = {
                "email": "test@multiagent.com",
                "password": "Test123!@#",
                "name": "Test User"
            }
            
            register_response = await client.post(
                f"{base_url}/api/auth/register",
                json=register_data
            )
            
            if register_response.status_code == 200:
                print("✅ User registered successfully")
            elif register_response.status_code == 400:
                print("ℹ️ User already exists, proceeding to login")
            
            # Login
            login_data = {
                "username": "test@multiagent.com",
                "password": "Test123!@#"
            }
            
            login_response = await client.post(
                f"{base_url}/api/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"✅ Authentication successful")
            
            # Test task extraction
            print("\n🤖 Testing Multi-Agent Task Extraction...")
            print("  Step 1: Sending request to API")
            print("  Step 2: Task Extractor Agent processes text")
            print("  Step 3: JSON Validator Agent ensures valid JSON")
            print("  Step 4: Returning structured tasks")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{base_url}/api/tasks/extract",
                json=test_data,
                headers=headers,
                timeout=60.0  # Give enough time for multi-agent processing
            )
            
            print(f"\n📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("isSuccess"):
                    data = result.get("data", {})
                    tasks = data.get("tasks", [])
                    
                    print(f"\n✅ Successfully extracted {len(tasks)} task(s)!")
                    print("\n📋 Extracted Tasks:")
                    print("=" * 60)
                    
                    for i, task in enumerate(tasks, 1):
                        print(f"\n[Task {i}]")
                        print(f"Title: {task.get('title', 'N/A')}")
                        print(f"Description: {task.get('description', 'N/A')[:100]}...")
                        print(f"Priority: {task.get('priority', 'unknown').upper()}")
                        print(f"Due Date: {task.get('dueDate', 'Not specified')}")
                        
                        if task.get('reference'):
                            print(f"Reference: {task['reference']}")
                        
                        subtasks = task.get('subTasks', [])
                        if subtasks:
                            print(f"Sub-tasks ({len(subtasks)}):")
                            for st in subtasks:
                                print(f"  ✓ {st.get('title', 'N/A')} ({st.get('estimatedMin', 0)} min)")
                    
                    print("\n" + "=" * 60)
                    
                    # Validate JSON structure
                    print("\n🔍 Validating JSON Structure:")
                    if tasks:
                        print("✅ Valid task structure returned")
                        print(f"Sample structure: {json.dumps(tasks[0], indent=2, ensure_ascii=False)[:300]}...")
                else:
                    print(f"❌ API returned error: {result.get('message', 'Unknown error')}")
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to API. Make sure the server is running:")
            print("   python3 -m uvicorn app.main:app --reload")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            print(traceback.format_exc())
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️  Note: Make sure the API server is running before running this test")
    print("   Run: python3 -m uvicorn app.main:app --reload")
    input("\nPress Enter to continue with the test...")
    
    asyncio.run(test_api_integration())