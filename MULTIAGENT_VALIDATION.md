# Multi-Agent JSON Validation System

## Overview

This system implements a true multi-agent architecture for robust task extraction with iterative JSON validation. It ensures that the AI-generated output is always valid JSON through multi-turn conversation refinement.

## Architecture

### 1. Task Extractor Agent (`app/core/ai/task_extractor.py`)
- **Role**: Primary agent for extracting tasks from unstructured text
- **Model**: HyperClova X HCX-007 (Thinking Model)
- **Strategy**: Uses prompt engineering to guide JSON generation
- **Features**:
  - User profile integration for personalized task extraction
  - Thinking effort configuration (medium by default for balanced performance)
  - Structured prompt templates for consistent output

### 2. JSON Validator Agent (`app/core/ai/json_validator.py`)
- **Role**: Ensures valid JSON output through iterative refinement
- **Strategy**: Multi-turn conversation with up to 3 attempts
- **Features**:
  - Local validation with JSON parsing
  - Automatic cleaning of common issues (markdown blocks, trailing commas)
  - AI-powered refinement when validation fails
  - Iterative improvement through multi-turn dialogue

## How It Works

### Step 1: Task Extraction
The Task Extractor Agent receives unstructured text and uses HyperClova's thinking model to extract tasks:

```python
# Extract with thinking model
response = await self.ai_client.chat_completion(
    messages=messages,
    max_completion_tokens=4096,
    thinking_effort="medium"  # Balanced performance
)
```

### Step 2: JSON Validation
The JSON Validator Agent ensures the output is valid JSON:

```python
# Multi-turn validation with max 3 attempts
success, parsed_json, final_content = await self.validator.ensure_valid_json(
    response["content"],
    expected_format,
    max_attempts=3
)
```

### Step 3: Iterative Refinement
If JSON validation fails, the validator requests refinement from the AI:

1. **Attempt 1**: Validate original output
2. **Attempt 2**: If invalid, request AI to fix JSON issues
3. **Attempt 3**: Final attempt with additional cleaning

### Step 4: Fallback Handling
If all validation attempts fail, the system falls back to basic task generation to ensure the user always gets a response.

## Configuration

### HyperClova Settings
- **Model**: HCX-007 (Thinking Model)
- **Max Completion Tokens**: 
  - Default: 10240 (medium thinking effort)
  - High: 20480 (for complex tasks)
- **Thinking Effort Levels**:
  - `none`: No thinking process
  - `low`: Quick analysis (5120 tokens)
  - `medium`: Balanced (10240 tokens) - **Default**
  - `high`: Deep analysis (20480 tokens)

### JSON Validation Settings
- **Max Attempts**: 3 (configurable)
- **Cleaning Operations**:
  - Remove markdown code blocks
  - Fix trailing commas
  - Handle nested structures

## API Integration

The multi-agent system is integrated into the task extraction API endpoint:

```python
# app/api/tasks.py
@router.post("/extract")
async def extract_tasks(request: TaskExtractRequest):
    extractor = TaskExtractor(api_key=api_key)
    # Multi-agent extraction with validation
    extracted_tasks = await extractor.extract_tasks(
        request.originalText, 
        user_profile
    )
```

## Testing

### Unit Tests
- `test_json_validation.py`: Tests JSON validation without API calls
- `test_multiagent_demo.py`: Demonstrates full multi-agent workflow

### Integration Tests
- `test_api_integration.py`: Tests the complete API with multi-agent system

### Running Tests
```bash
# Test JSON validation locally
python3 test_json_validation.py

# Test full multi-agent demo
python3 test_multiagent_demo.py

# Test API integration (requires server running)
python3 -m uvicorn app.main:app --reload
python3 test_api_integration.py
```

## Example Output

Input text:
```
내일까지 프로젝트 제안서 작성하기 - 매우 중요!
버그 수정: 로그인 API 500 에러 해결 (긴급)
```

Multi-agent processing:
1. **Task Extractor**: Generates JSON with tasks
2. **JSON Validator**: Validates and refines if needed
3. **Result**: Clean, valid JSON output

```json
{
  "tasks": [
    {
      "title": "프로젝트 제안서 작성",
      "priority": "HIGH",
      "dueDate": "2025-08-10T23:59:59",
      "subTasks": [
        {"title": "초안 작성", "estimatedMin": 120},
        {"title": "검토 및 수정", "estimatedMin": 60}
      ]
    },
    {
      "title": "로그인 API 버그 수정",
      "priority": "URGENT",
      "subTasks": [
        {"title": "에러 분석", "estimatedMin": 30},
        {"title": "코드 수정", "estimatedMin": 45}
      ]
    }
  ]
}
```

## Benefits

1. **Reliability**: Ensures valid JSON output through iterative validation
2. **Flexibility**: Handles various JSON formatting issues automatically
3. **User Experience**: Always provides a response, even with fallback
4. **Scalability**: Easy to add more validation agents or refinement strategies
5. **True Multi-Agent**: Agents work together through multi-turn conversations

## Future Enhancements

1. Add more specialized validation agents (schema validation, business logic)
2. Implement agent communication protocols for complex scenarios
3. Add learning capabilities to improve over time
4. Support for more output formats beyond JSON
5. Performance optimization with agent result caching