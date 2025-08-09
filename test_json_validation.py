#!/usr/bin/env python3
"""
Quick test of JSON validation functionality
"""
import asyncio
import os
from app.core.ai.json_validator import JsonValidatorAgent

async def test_validation():
    """Test JSON validation without API calls"""
    
    print("Testing JSON Validator Agent (without API)")
    print("=" * 50)
    
    validator = JsonValidatorAgent(api_key=None)  # No API calls
    
    # Test local validation only
    test_cases = [
        {
            "name": "Valid JSON",
            "content": '{"tasks": [{"title": "Test", "priority": "HIGH"}]}'
        },
        {
            "name": "JSON with markdown blocks",
            "content": '```json\n{"tasks": [{"title": "Meeting", "priority": "MID"}]}\n```'
        },
        {
            "name": "JSON with trailing comma",
            "content": '{"tasks": [{"title": "Report", "priority": "LOW"},]}'
        },
        {
            "name": "Nested JSON structure",
            "content": '''{"tasks": [
                {
                    "title": "Project Setup",
                    "priority": "HIGH",
                    "subTasks": [
                        {"title": "Initialize repo", "estimatedMin": 15},
                        {"title": "Setup CI/CD", "estimatedMin": 60}
                    ]
                }
            ]}'''
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        is_valid, parsed, error = validator.validate_json(test['content'])
        
        if is_valid:
            print(f"  ✅ Valid JSON")
            if 'tasks' in parsed:
                print(f"  Tasks found: {len(parsed['tasks'])}")
                for task in parsed['tasks']:
                    print(f"    - {task.get('title', 'No title')}: {task.get('priority', 'No priority')}")
        else:
            print(f"  ❌ Invalid: {error}")
            
            # Try cleaning
            cleaned = validator._clean_json_string(test['content'])
            is_valid2, parsed2, error2 = validator.validate_json(cleaned)
            
            if is_valid2:
                print(f"  ✅ Fixed after cleaning!")
                if 'tasks' in parsed2:
                    print(f"  Tasks found: {len(parsed2['tasks'])}")
            else:
                print(f"  ❌ Still invalid after cleaning: {error2}")

if __name__ == "__main__":
    asyncio.run(test_validation())