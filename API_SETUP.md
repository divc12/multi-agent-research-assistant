# API Integration & Configuration Guide

Complete guide for setting up and configuring the Multi-Agent Research Assistant with real Tavily Search and OpenAI APIs.

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Configuration](#api-configuration)
3. [Validation Modes](#validation-modes)
4. [API Testing](#api-testing)
5. [Cost Optimization](#cost-optimization)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Dependencies
```bash
pip install tavily-python openai python-dotenv
```

### 2. Set Environment Variables
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:TAVILY_API_KEY="tvly-..."

# Linux/Mac
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

Or create a `.env` file:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 3. Verify Integration Active
The integrations are **already active** with graceful fallback:
- ✅ Tavily client initialized ([research_agent.py](app/agents/research_agent.py#L18-L21))
- ✅ OpenAI integrations commented out (see agent files)
- ✅ Environment loading active ([main.py](main.py#L10-L11))

### 4. Test Connection
```bash
python main.py
User: What's going on with Apple?
```
You should see real-time Tavily results with sources.

---

## API Configuration

### Service-to-Agent Mapping

| Agent | Service | Model | Purpose |
|-------|---------|-------|---------|
| **Clarity Agent** | OpenAI | GPT-4o-mini | Query analysis (commented) |
| **Research Agent** | **Tavily** | Search API | **Web research (ACTIVE)** |
| **Validator Agent** | OpenAI | GPT-4o-mini | Quality validation (commented) |
| **Synthesis Agent** | OpenAI | GPT-4o | Response generation (commented) |

### Current Implementation Status

✅ **Tavily Integration**: ACTIVE  
⏸️ **OpenAI Integration**: Commented out (429 rate limit issues)  
✅ **Mock Data Fallback**: Active when Tavily unavailable  
✅ **Rule-Based Logic**: Active for clarity/validation

---

## Validation Modes

### Overview
The system has TWO modes that can be toggled in `config.py`:

### MODE 1: Normal Mode (Production)
**Use for**: Real-world queries, production deployment

**Settings** in `config.py`:
```python
STRICT_VALIDATION_MODE = False  # Normal confidence threshold (6+)
```

**Behavior**:
- Tavily searches business news domains only
- Validates results are company-related
- **Confidence threshold: 6+** to pass validation
- High-quality results bypass retry loop
- Optimized for real user queries

**Example**:
```
User: What's going on with Apple?
→ Tavily search → Confidence 9.5 → No retries → Response with sources
```

---

### MODE 2: Strict Validation Mode (Demo/Testing)
**Use for**: Demonstrating validation retry loop (Test Case 5.1)

**Settings** in `config.py`:
```python
STRICT_VALIDATION_MODE = True  # Strict confidence threshold (8+)
```

**Behavior**:
- Same Tavily search with **higher quality bar**
- **Confidence threshold: 8+** to pass validation
- Low-confidence results trigger retry loop (up to 3 attempts)
- Demonstrates robust error handling

**Example**:
```
User: What's going on with FakeXYZCorp999?
→ Tavily search → Confidence 6.2 < 8
→ [STRICT MODE] Forcing confidence to 3
→ Retry 1: Confidence 3 < 8 → insufficient
→ Retry 2: Confidence 3 < 8 → insufficient
→ Retry 3: Confidence 3 < 8 → insufficient
→ Error message: "I don't have sufficient data..."
```

---

### How to Switch Modes

**Step 1: Open config.py**
```bash
code config.py
```

**Step 2: Change line 8**
```python
# For Production
STRICT_VALIDATION_MODE = False

# For Demo/Test Case 5.1
STRICT_VALIDATION_MODE = True
```

**Step 3: Save and Run**
```bash
python main.py
```

---

### Configuration Details

#### Business Domains (Always Active)
Tavily only searches these trusted sources:
```python
TAVILY_SEARCH_DOMAINS = [
    "bloomberg.com", "reuters.com", "cnbc.com",
    "wsj.com", "ft.com", "forbes.com",
    "businessinsider.com", "marketwatch.com",
    "finance.yahoo.com", "seekingalpha.com",
    "fool.com", "benzinga.com", "thestreet.com",
    "investing.com", "barrons.com"
]
```

#### Company Keyword Detection
Results must contain business terms:
```python
COMPANY_KEYWORDS = [
    "stock", "shares", "trading", "market", "ceo", "company",
    "revenue", "earnings", "profit", "quarterly", "annual",
    "nasdaq", "nyse", "ipo", "acquisition", "merger", "business"
]
```

#### Validation Thresholds
```python
STRICT_CONFIDENCE_THRESHOLD = 8  # Must have 8+ in strict mode
NORMAL_CONFIDENCE_THRESHOLD = 6  # 6+ in normal mode
MIN_ANSWER_LENGTH = 50           # Reject answers < 50 chars
```

---

## API Testing

### Test Scenarios by Mode

#### Normal Mode Tests (STRICT_VALIDATION_MODE = False)

**Test 1: Real Company Query**
```
User: What's going on with Apple?
```
**Expected:**
- Tavily search succeeds
- Confidence ~9.5 (high quality)
- **No retries** (passes validation immediately)
- Real-time news with sources
- Natural language response

**Verification:**
- ✅ Response contains recent, real news
- ✅ Sources cited from Tavily
- ✅ No console retries
- ✅ No mock data phrases

---

**Test 2: Multi-Turn Conversation**
```
Turn 1: What's happening with Tesla?
Turn 2: What about their stock?
Turn 3: Any recent developments?
```
**Expected:**
- All 3 turns use Tesla context
- Tavily searches include conversation history
- Targeted responses (stock-only for turn 2)
- No clarification requests

---

**Test 3: High-Quality Unknown Company**
```
User: What about ZoomerMedia?
```
**Expected:**
- Tavily finds real company (ZoomerMedia Limited)
- Confidence ~8+ (has company keywords)
- **No retries** (quality is sufficient)
- Returns valid business information

---

#### Strict Mode Tests (STRICT_VALIDATION_MODE = True)

**Test 4: Low-Quality Results Retry**
```
User: What's going on with XYZCorp999?
```
**Expected:**
- Tavily searches but finds vague results
- Confidence ~6 < 8 (below strict threshold)
- Console shows: `[STRICT MODE] Confidence 6.2 < 8, will trigger validation retry`
- **3 retry attempts** visible in console
- Final error message after 3 attempts

**Console Output:**
```
[STRICT MODE] Confidence 6.22698052 < 8, will trigger validation retry
[VALIDATOR] Confidence 3 < 8 (STRICT mode)
[STRICT MODE] Confidence 6.22698052 < 8, will trigger validation retry
[VALIDATOR] Confidence 3 < 8 (STRICT mode)
[STRICT MODE] Confidence 6.22698052 < 8, will trigger validation retry
[VALIDATOR] Confidence 3 < 8 (STRICT mode)
Assistant: I don't have sufficient data available for that query...
```

---

**Test 5: Real Company in Strict Mode**
```
User: What's going on with Apple?
```
**Expected:**
- Tavily finds excellent Apple results
- Confidence ~9.5 ≥ 8 (exceeds strict threshold)
- **No retries** (quality is exceptional)
- Returns current Apple news

**Key Insight:** Strict mode doesn't force retries on ALL queries—only those below threshold 8.

---

### Fallback Behavior Tests

#### Test 6: Tavily Disabled (Mock Fallback)
**Setup:** Comment out Tavily client in `research_agent.py` lines 18-21

**Input:**
```
User: What's going on with Apple?
```
**Expected:**
- Console: `[INFO] Tavily unavailable, using mock data`
- Returns mock Apple data (Vision Pro, services revenue)
- Response includes mock phrases
- No Tavily sources

---

#### Test 7: Invalid Query (Clarity Check)
**Input:**
```
User: tell me more
```
**Expected:**
- Rule-based clarity marks as "needs_clarification"
- Interrupt: "Please clarify which company you are referring to:"
- After clarification, proceeds normally

---

### Performance Metrics

| Metric | Normal Mode | Strict Mode |
|--------|-------------|-------------|
| **Tavily Search** | Active | Active |
| **Confidence Threshold** | 6+ | 8+ |
| **Retry Frequency** | Rare (~5% queries) | Common (~40% queries) |
| **Avg Response Time** | 2-5s | 3-8s (with retries) |
| **Cost per Query** | ~$0.001 (Tavily only) | ~$0.001-0.003 (retries) |

---

## Cost Optimization

### Current Cost Structure

**With Tavily Only (OpenAI commented):**
- Tavily: ~$0.001 per search
- OpenAI: $0 (commented out)
- **Total: $0.001-0.003 per query** (with retries)

**If OpenAI Enabled:**
| Agent | Service | Cost per Call |
|-------|---------|---------------|
| Clarity | GPT-4o-mini | ~$0.0001 |
| Validator | GPT-4o-mini | ~$0.0001 |
| Synthesis | GPT-4o | ~$0.01 |
| Research | Tavily | ~$0.001 |

Total with OpenAI: ~$0.011-0.013 per query

### Optimization Tips

1. **Reduce Tavily Search Depth**
   ```python
   # In research_agent.py line 64
   search_depth="basic",  # Instead of "advanced"
   ```
   Saves API credits, faster responses

2. **Cache Frequent Queries**
   ```python
   # Add simple cache
   query_cache = {}
   if query in query_cache:
       return query_cache[query]
   ```

3. **Use Stricter Domain Filtering**
   ```python
   # Reduce domains in config.py
   TAVILY_SEARCH_DOMAINS = ["bloomberg.com", "reuters.com", "cnbc.com"]
   ```

4. **Lower Max Results**
   ```python
   # In research_agent.py line 65
   max_results=3,  # Instead of 5
   ```

---

## Troubleshooting

### "Tavily search failed"
**Symptoms:** Console shows `[INFO] Tavily unavailable, using mock data`

**Solutions:**
1. Check API key is correct
   ```bash
   echo $env:TAVILY_API_KEY  # Windows
   echo $TAVILY_API_KEY      # Linux/Mac
   ```
2. Verify internet connection
3. Check Tavily account has credits: https://app.tavily.com
4. Look for specific error in console output

---

### "No retries in strict mode"
**Symptoms:** `STRICT_VALIDATION_MODE=True` but no retry loop visible

**Cause:** Query has high confidence (≥8)

**Solutions:**
1. Check console for confidence score
2. Try queries for unknown companies: "XYZCorp999", "FakeCompany123"
3. Verify `config.py` line 8 is `STRICT_VALIDATION_MODE = True`
4. Look for `[STRICT MODE]` messages in console

---

### "Results still using mock data"
**Symptoms:** Responses include "Cybertruck", "Vision Pro" (mock phrases)

**Causes:**
1. Tavily API key missing or invalid
2. Tavily client not initialized
3. Exception in Tavily search

**Solutions:**
1. Verify `.env` file exists with `TAVILY_API_KEY=...`
2. Check lines 18-21 in `research_agent.py` are uncommented
3. Run with `python -u main.py` to see all console output
4. Check for exception messages

---

### "Response too slow"
**Symptoms:** Queries take >10 seconds

**Causes:**
- Tavily "advanced" search depth
- Multiple retries in strict mode
- Network latency

**Solutions:**
1. Use `search_depth="basic"` for faster searches
2. Switch to normal mode (`STRICT_VALIDATION_MODE = False`)
3. Reduce `max_results` to 3
4. Check internet connection speed

---

### "OpenAI rate limit exceeded"
**Symptoms:** `429 Too Many Requests` error

**Note:** OpenAI integration is currently **commented out** to avoid this issue.

**If you uncomment OpenAI:**
1. Add rate limiting with `tenacity`:
   ```python
   from tenacity import retry, wait_exponential
   
   @retry(wait=wait_exponential(min=1, max=10))
   def call_openai():
       # Your OpenAI call
   ```
2. Upgrade OpenAI plan for higher limits
3. Add delays between calls
4. Use mock data for development

---

## Quick Smoke Test

Minimal test to verify setup:

```bash
python main.py

# Test 1: Real-time search (Normal mode)
User: What's going on with Apple?
Expected: Current Apple news with Tavily sources
✅ No "[STRICT MODE]" in console
✅ Real data, not mock

# Test 2: Strict mode retry
# Edit config.py: STRICT_VALIDATION_MODE = True
User: What about XYZCorp999?
Expected: Console shows 3 retry attempts
✅ "[STRICT MODE]" messages visible
✅ 3 "[VALIDATOR]" lines
✅ Final error message

# Exit
User: exit
```

---

## Summary

### Quick Reference

| Feature | Normal Mode | Strict Mode |
|---------|-------------|-------------|
| **Config Setting** | `STRICT_VALIDATION_MODE = False` | `STRICT_VALIDATION_MODE = True` |
| **Confidence Threshold** | 6+ | 8+ |
| **Tavily Search** | ✓ Active | ✓ Active |
| **Domain Filtering** | ✓ 15 business sources | ✓ 15 business sources |
| **Retry Loop** | Rare | Common |
| **Use Case** | Production queries | Test Case 5.1 demo |
| **Cost** | ~$0.001/query | ~$0.001-0.003/query |

### Toggle in One Line
Edit `config.py` line 8:
```python
STRICT_VALIDATION_MODE = False  # Production
STRICT_VALIDATION_MODE = True   # Demo/Testing
```

### Key Files
- **config.py** - All configuration settings
- **research_agent.py** - Tavily integration (lines 18-116)
- **validator_agent.py** - Threshold logic (line 101)
- **.env** - API keys (create from template)

---

For mock data testing without APIs, see [TESTING.md](TESTING.md).
