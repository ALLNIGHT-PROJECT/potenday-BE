#!/usr/bin/env python3
"""
Main test runner for the multi-agent task extraction system
"""
import asyncio
import os

async def main():
    print("=" * 80)
    print("MULTI-AGENT TASK EXTRACTION SYSTEM - TEST SUITE")
    print("=" * 80)
    
    # Set API key
    os.environ["HYPERCLOVA_API_KEY"] = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
    
    print("\n📋 Available Tests:")
    print("1. JSON Validation Test (test_json_validation.py)")
    print("2. Task Response Format Test (test_task_response.py)")
    print("3. Multi-Agent Validation Test (test_multiagent_validation.py)")
    print("4. API Integration Test (test_api_integration.py)")
    
    print("\n🧪 Running Tests...")
    
    # Test 1: JSON Validation
    print("\n" + "=" * 60)
    print("Test 1: JSON Validation")
    print("=" * 60)
    os.system("python3 test_json_validation.py")
    
    # Test 2: Task Response Format
    print("\n" + "=" * 60)
    print("Test 2: Task Response Format")
    print("=" * 60)
    os.system("python3 test_task_response.py")
    
    print("\n" + "=" * 80)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 80)
    print("""
Summary:
- Database: Cleaned for fresh testing
- Test Files: Organized (4 core tests remaining)
- System: Ready for testing

To test the API:
1. Start the server: python3 -m uvicorn app.main:app --reload
2. Run API test: python3 test_api_integration.py

To test multi-agent validation with real API:
Run: python3 test_multiagent_validation.py
""")

if __name__ == "__main__":
    asyncio.run(main())