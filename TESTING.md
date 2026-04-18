# Comprehensive Testing Guide

This document provides comprehensive testing strategies for the Multi-Agent Research Assistant.

## Test Categories

### 1. Basic Functionality Tests

#### Test 1.1: Simple Company Query (Happy Path)
**Input:**
```
User: What's going on with Apple?
```
**Expected:**
- Clarity Agent marks as "clear"
- Research Agent finds Apple data
- Confidence score = 9
- Validator marks as "sufficient"
- Response includes news, stock, and developments

**Verification:**
- ✅ Response contains all three data fields
- ✅ No validation loop triggered
- ✅ Company name "Apple" appears in response

---

#### Test 1.2: Each Company
**Inputs:**
```
User: Tell me about Tesla
User: What's happening with Microsoft?
User: How is Apple doing?
```
**Expected:**
- All three companies return complete data
- Confidence scores: Apple=9, Tesla=8, Microsoft=9
- Proper company-specific information in responses

---

### 2. Interrupt & Clarification Tests

#### Test 2.1: Vague Query (Interrupt Flow)
**Input:**
```
User: tell me about that company
```
**Expected:**
- Clarity Agent marks as "needs_clarification"
- Graph interrupts with clarification request
- Message: "Please clarify which company you are referring to:"
- Waits for user input

**Follow-up:**
```
User: Apple
```
**Expected:**
- Graph resumes from Clarity Agent
- Proceeds with normal research flow
- Returns Apple data

**Verification:**
- ✅ Interrupt triggered
- ✅ Clarification message displayed
- ✅ Graph resumed correctly
- ✅ Final response contains Apple data

---

#### Test 2.2: Short Ambiguous Query
**Input:**
```
User: news
```
**Expected:**
- Triggers clarification (no company mentioned, very short)
- After clarification, returns requested company info

---

### 3. Multi-Turn Conversation Tests

#### Test 3.1: Follow-up Question (Context Retention)
**Turn 1:**
```
User: What's going on with Tesla?
```
**Expected:** Full Tesla summary

**Turn 2:**
```
User: What about their stock?
```
**Expected:**
- System recognizes "their" refers to Tesla (from history)
- Returns only stock info: "Trading at $242, volatile quarter"
- Does NOT ask for clarification

**Verification:**
- ✅ Context maintained across turns
- ✅ No clarification requested on turn 2
- ✅ Correct company identified from history
- ✅ Targeted response (stock only, not full summary)

---

#### Test 3.2: Extended Conversation
**Turn 1:**
```
User: What's happening with Microsoft?
```
**Turn 2:**
```
User: What about their recent news?
```
**Turn 3:**
```
User: And developments?
```
**Expected:**
- All 3 turns use Microsoft context
- Turn 2 returns only news
- Turn 3 returns only developments
- No clarification requests

---

### 4. Query Intent Classification Tests

#### Test 4.1: Stock-Specific Query
**Input:**
```
User: What's Apple's stock price?
```
**Expected:**
- Response contains ONLY stock info
- Format: "Regarding Apple: Trading at $195, up 45% YTD"
- Does NOT include news or developments

---

#### Test 4.2: News-Specific Query
**Input:**
```
User: What's the latest news about Tesla?
```
**Expected:**
- Response contains ONLY recent news
- Format: "Tesla news: Cybertruck deliveries ramping up..."
- Does NOT include stock or developments

---

#### Test 4.3: Development-Specific Query
**Input:**
```
User: What is Microsoft working on?
```
**Expected:**
- Response contains ONLY developments
- Format: "Microsoft developments: OpenAI partnership deepening..."
- Does NOT include news or stock

---

### 5. Validator Logic Tests

#### Test 5.1: Low Confidence (Unknown Company)
**Input:**
```
User: What's going on with Google?
```
**Expected:**
- Research returns error (company not in mock data)
- Confidence score = 3
- Validator marks as "insufficient"
- Validator → Research loop triggered (up to 3 times)
- After 3 attempts, synthesis with error message
- Final response: "I don't have data available for that company. Please try asking about Apple, Tesla, or Microsoft."

**Verification:**
- ✅ research_attempts increments correctly
- ✅ Loop exits after 3 attempts
- ✅ Error message displayed
- ✅ No crash or infinite loop

---

#### Test 5.2: Missing Specific Data (Simulated)
To test this, you'd need to temporarily modify mock data to remove a field, e.g., remove `stock_info` from Tesla:

**Modified mock data:**
```python
"Tesla": {
    "recent_news": "Cybertruck deliveries ramping up...",
    # "stock_info": "",  # REMOVED for testing
    "key_developments": "FSD v12 rollout...",
    "confidence": 8
}
```

**Input:**
```
User: What's Tesla's stock price?
```
**Expected:**
- Validator detects missing stock_info
- Marks as "insufficient"
- Triggers research retry
- After retries, synthesis with incomplete data

---

### 6. Edge Case Tests

#### Test 6.1: Empty Query
**Input:**
```
User: 
```
**Expected:**
- Clarity marks as "needs_clarification"
- Interrupt triggered

---

#### Test 6.2: Case Insensitivity
**Inputs:**
```
User: APPLE
User: apple
User: ApPlE
```
**Expected:**
- All recognized correctly
- Same response for all variations

---

#### Test 6.3: Company Name in Different Positions
**Inputs:**
```
User: Apple stock price
User: Stock price for Apple
User: What's the stock, for Apple?
```
**Expected:**
- All recognized as Apple queries
- All return stock-specific info

---

### 7. State Management Tests

#### Test 7.1: State Reset Between Queries
**Turn 1:**
```
User: What's going on with Apple?
```
**Turn 2:**
```
User: What about Tesla?
```
**Expected:**
- Turn 2 should use Tesla, NOT Apple
- State properly resets/updates between independent queries
- No crosstalk between different company queries

---

#### Test 7.2: Message History Accumulation
**Conversation:**
```
User: Tesla
Assistant: <response>
User: What about their stock?
Assistant: <response>
User: And news?
Assistant: <response>
```
**Verification:**
- Check that message history grows correctly
- Each turn adds both user and assistant messages
- Context available for all subsequent queries

---

## Running Tests Manually

### Setup
```bash
cd multi-agent-research-assistant
python main.py
```

### Test Execution

1. **Run each test case** from the categories above
2. **Record results** in a table:

| Test ID | Input | Expected | Actual | Pass/Fail |
|---------|-------|----------|--------|-----------|
| 1.1 | What's going on with Apple? | Full summary | ... | ✅ |
| 2.1 | tell me about that company | Interrupt | ... | ✅ |
| ... | ... | ... | ... | ... |

3. **Check for errors** in terminal output
4. **Verify state transitions** by adding debug prints if needed

---

## Automated Testing (Future Enhancement)

### Unit Test Example Structure

```python
# tests/test_clarity_agent.py
import pytest
from app.agents.clarity_agent import clarity_agent

def test_clarity_with_company_name():
    state = {"query": "What's going on with Apple?", "messages": []}
    result = clarity_agent(state)
    assert result["clarity_status"] == "clear"

def test_clarity_without_company():
    state = {"query": "tell me about that company", "messages": []}
    result = clarity_agent(state)
    assert result["clarity_status"] == "needs_clarification"

def test_clarity_with_context():
    state = {
        "query": "what about their stock?",
        "messages": [
            ("user", "What's going on with Tesla?"),
            ("assistant", "Tesla news...")
        ]
    }
    result = clarity_agent(state)
    assert result["clarity_status"] == "clear"
```

---

## Integration Test Scenarios

### Scenario A: Complete Happy Path
```
User: What's going on with Apple?
→ Clarity: clear
→ Research: finds Apple (confidence=9)
→ Validator: sufficient
→ Synthesis: full summary
→ END
```

### Scenario B: Interrupt and Resume
```
User: tell me more
→ Clarity: needs_clarification
→ Interrupt: "Please clarify..."
User: Microsoft
→ Clarity: clear
→ Research: finds Microsoft
→ Validator: sufficient
→ Synthesis: full summary
→ END
```

### Scenario C: Validation Loop
```
User: What's happening with Google?
→ Clarity: clear
→ Research: error (confidence=3)
→ Validator: insufficient (attempt 1)
→ Research: error (confidence=3)
→ Validator: insufficient (attempt 2)
→ Research: error (confidence=3)
→ Validator: insufficient (attempt 3)
→ Synthesis: error message
→ END
```

### Scenario D: Multi-Turn with Context
```
User: What's going on with Tesla?
→ Full pipeline → Tesla summary

User: What about their stock?
→ Clarity: clear (context from history)
→ Research: finds Tesla
→ Validator: sufficient
→ Synthesis: stock-only response
→ END
```

---

## Performance Metrics

Track these metrics during testing:

- **Response Time**: How long each query takes
- **Accuracy**: Does response match expected output?
- **Context Retention**: Follow-up questions work correctly?
- **Error Handling**: Graceful degradation on unknown companies?
- **Loop Prevention**: Validation doesn't loop infinitely?

---

## Debugging Tips

### Enable Debug Mode
Add print statements to agents:

```python
def clarity_agent(state: dict) -> dict:
    print(f"[DEBUG] Clarity Agent - Query: {state['query']}")
    result = # ... logic
    print(f"[DEBUG] Clarity Agent - Status: {result['clarity_status']}")
    return result
```

### Inspect State
Add state dumping in main.py:

```python
import json
result = graph.invoke(state)
print(json.dumps(result, indent=2, default=str))
```

### Trace Graph Execution
Use LangSmith (if configured) or add logging to routing functions.

---

## Test Coverage Checklist

- [ ] All 3 companies (Apple, Tesla, Microsoft)
- [ ] Unknown company (triggers error handling)
- [ ] Interrupt mechanism
- [ ] Multi-turn conversation (at least 2 turns)
- [ ] Query intent classification (stock, news, development)
- [ ] Follow-up questions with context
- [ ] Validation loop (low confidence)
- [ ] Case insensitivity
- [ ] Empty/vague queries
- [ ] State reset between queries
- [ ] Message history accumulation
- [ ] All routing paths (clarity → research, research → validator, validator → research, validator → synthesis)

---

## Quick Smoke Test

Minimal test to verify basic functionality:

```bash
python main.py

# Test 1: Happy path
User: What's going on with Apple?
Expected: Full Apple summary

# Test 2: Interrupt
User: tell me more
Expected: Clarification request
User: Tesla
Expected: Full Tesla summary

# Test 3: Follow-up
User: What about their stock?
Expected: Tesla stock info only

# Test 4: Unknown company
User: What's happening with Google?
Expected: "I don't have data available..."

# Exit
User: exit
```

If all 4 tests pass, core functionality is working! ✅
