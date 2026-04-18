# Multi-Agent Research Assistant (LangGraph)

A multi-agent research assistant built with LangGraph that coordinates specialized agents to gather and synthesize company information. The system maintains conversation context across turns and asks for human clarification when queries are ambiguous.

## Setup

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies
- `langgraph` - Multi-agent orchestration framework
- `langchain-core` - Core LangGraph utilities
- `tavily-python` - Tavily Search API client (for real-time research)
- `python-dotenv` - Environment variable management

### Optional Dependencies
- `openai` - OpenAI GPT integration (currently commented out)
- `jupyter` - For running `visualize_langgraph.ipynb`

### Environment Setup
Create a `.env` file in the project root:
```env
TAVILY_API_KEY=tvly-your-api-key-here
# OPENAI_API_KEY=sk-your-key-here  # Optional, currently unused
```

Get a free Tavily API key at: https://app.tavily.com

## How to Run

### Basic Setup (Mock Data Only)
```bash
# Ensure virtual environment is activated
python main.py
```

### With Tavily Search API (Recommended)
```bash
# Create .env file with your Tavily API key
echo "TAVILY_API_KEY=tvly-your-api-key" > .env

# Run the application
python main.py
```

The application will start an interactive chat session. Type your questions about companies and type `exit` to quit.

### Example Usage (with Tavily)

```
User: What's going on with Apple?
Assistant: Apple continues strong iPhone sales, especially in China, and faces 
challenges like supply chain complexities and AI integration. The company navigates 
geopolitical tensions and maintains a premium brand.

Sources:
1. Apple bears proven wrong yet again as iPhone defies China slump narrative - https://www.cnbc.com/...
2. Five key questions Apple faces entering its second half-century - https://www.cnbc.com/...
3. Apple: Trending News, Latest Updates, Analysis - Bloomberg

User: What about their stock price?
Assistant: Regarding Apple: [Real-time stock information from Tavily]

User: exit
```

**Note**: Without Tavily API key, system falls back to mock data for Apple, Tesla, and Microsoft.

## Architecture

The system uses 4 specialized agents in a LangGraph state graph:

1. **Clarity Agent**: Determines if the query is specific enough (rule-based)
2. **Research Agent**: Retrieves company information via **Tavily Search API** (active)
3. **Validator Agent**: Validates if findings answer the query adequately (rule-based)
4. **Synthesis Agent**: Produces the final user-facing response (template-based)

### Current Implementation Status
- ✅ **Tavily Search API**: Active for real-time web research
- ⏸️ **OpenAI GPT Models**: Commented out (429 rate limiting issues)
- ✅ **Rule-based Logic**: Active fallback for clarity, validation, synthesis
- ✅ **Mock Data**: Fallback when Tavily unavailable

### State Flow
```
Clarity → [Research ⇄ Validator] → Synthesis → END
           ↓
    Interrupt (if unclear)
```

## Assumptions

### Data Source
- **Primary**: Tavily Search API for real-time company research (active)
- **Fallback**: Mock data for three companies (Apple, Tesla, Microsoft) when Tavily unavailable
- **LLM Integration**: OpenAI GPT code present but commented out due to 429 rate limit errors
- **Agent Logic**: Rule-based implementations active for clarity, validation, and synthesis
- Mock data is hardcoded in `data/mock_data.py`

### API Configuration
- **Tavily Search**: Active by default, searches 15 business news domains
- **OpenAI**: Commented out in all agent files due to 429 rate limit errors
  - Code is present and can be enabled by uncommenting integration sections
  - Would enable LLM-based clarity analysis, validation, and natural language synthesis
  - Currently using rule-based and template-based fallbacks
- **Environment Variables**: API keys loaded from `.env` file via `python-dotenv`
- **Graceful Degradation**: System falls back to mock data if Tavily API fails

### Conversation Context
- Message history is maintained in-memory for the session
- History resets when the application restarts
- Follow-up questions work by checking previous messages for company context

### Clarification Flow
- Interrupt triggers for vague queries without recognizable company names
- After clarification, the graph restarts from the Clarity Agent
- System assumes clarified input contains the company name

### Validation Logic
- **Validation Modes**: Two modes controlled by `config.py` (Normal: 6+ threshold, Strict: 8+ threshold)
- Validator checks if specific information types match the query intent
- Dynamic threshold based on `STRICT_VALIDATION_MODE` setting
- Maximum 3 research attempts before forcing synthesis
- Tavily results validated for company-related keywords and minimum answer length

### Query Understanding
- Company names are matched case-insensitively
- Specific keywords trigger targeted responses (e.g., "stock" → stock info only)
- Generic queries return full company summaries

## Project Structure

```
multi-agent-research-assistant/
├── main.py                      # Entry point and chat loop
├── config.py                    # Configuration settings (validation modes, thresholds)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── TESTING.md                   # Mock data testing guide
├── API_SETUP.md                 # API integration & configuration guide
├── .env.example                 # Environment variables template
├── graph.mmd                    # Mermaid graph visualization
├── visualize_langgraph.ipynb    # Interactive graph visualization notebook
├── app/
│   ├── graph.py                # LangGraph definition and routing
│   ├── state.py                # State schema (ResearchState)
│   ├── visualize_graph.py      # Graph visualization utility
│   └── agents/
│       ├── clarity_agent.py     # Query clarity checker (rule-based)
│       ├── research_agent.py    # Tavily Search integration (active)
│       ├── validator_agent.py   # Validation logic (rule-based)
│       └── synthesis_agent.py   # Response generation (template-based)
└── data/
    └── mock_data.py            # Mock research data (fallback)
```

## Graph Visualization

The project includes an interactive Jupyter notebook for visualizing the LangGraph architecture:

### Using the Visualization Notebook
```bash
# Install Jupyter if not already installed
pip install jupyter

# Launch the notebook
jupyter notebook visualize_langgraph.ipynb
```

The notebook ([visualize_langgraph.ipynb](visualize_langgraph.ipynb)) provides:
- **Interactive Mermaid diagrams** with multiple themes (default, dark mode)
- **PNG exports** (requires Graphviz installation)
- **HTML exports** for sharing visualizations
- **Color-coded nodes** showing agent flow and routing logic

## Testing & API Setup

### Testing Guides
- **[TESTING.md](TESTING.md)** - Comprehensive testing with mock data (no API keys needed)
- **[API_SETUP.md](API_SETUP.md)** - API integration, configuration modes, and real API testing

### Quick Smoke Test

```bash
python main.py

# Test 1: Happy path (uses Tavily if API key set, otherwise mock data)
User: What's going on with Apple?

# Test 2: Interrupt flow
User: tell me more
User: Tesla

# Test 3: Follow-up question
User: What about their stock?

# Test 4: Unknown company (triggers retry loop in strict mode)
User: What's happening with Google?

# Exit
User: exit
```

**Key Test Scenarios:**
- ✅ Basic company queries (Apple, Tesla, Microsoft)
- ✅ Real-time data from Tavily (if API key configured)
- ✅ Interrupt mechanism for vague queries
- ✅ Multi-turn conversation with context retention
- ✅ Query intent classification (stock, news, developments)
- ✅ Validation loop for missing data (up to 3 retries)
- ✅ Error handling for unknown companies
- ✅ Graceful fallback to mock data when API unavailable

**Modes:**
- With Tavily API key: Returns real-time company information
- Without API key: Falls back to mock data (Apple, Tesla, Microsoft only)

See [TESTING.md](TESTING.md) for detailed test cases and validation criteria.

## Beyond Expected Deliverable

### Enhanced Features Implemented

1. **Real-Time Web Research with Tavily**
   - Active integration with Tavily Search API for current company information
   - Searches 15 trusted business news domains (Bloomberg, Reuters, CNBC, etc.)
   - Returns AI-generated answers with source citations
   - Graceful fallback to mock data when API unavailable

2. **Intelligent Validation System**
   - Dual-mode configuration: Normal (6+ confidence) vs. Strict (8+ confidence)
   - Company keyword detection (18 business-related terms)
   - Minimum answer length validation (50 characters)
   - Configurable retry loop (up to 3 attempts) for quality assurance

3. **Context-Aware Follow-up Questions**
   - System remembers previously discussed companies across turns
   - Both tuple and LangGraph Message object formats are handled
   - Follow-up detection works even without explicit company mentions
   - Tavily searches include conversation context for better results

4. **Query Intent Classification**
   - Synthesis agent classifies queries by type (stock, news, developments)
   - Returns targeted responses rather than always dumping full data
   - Handles both Tavily (AI-generated) and mock (template-based) data structures

5. **Graph Visualization Tools**
   - `visualize_langgraph.ipynb`: Interactive Jupyter notebook with Mermaid diagrams
   - `visualize_graph.py`: Programmatic graph visualization utility
   - Multiple themes: default, dark mode with custom colors
   - Exports to `.mmd`, `.png`, and `.html` formats

6. **Comprehensive Configuration System**
   - `config.py`: Centralized settings for all validation parameters
   - Easy toggle between production and demo modes
   - Domain filtering, keyword lists, and thresholds all configurable
   - See [API_SETUP.md](API_SETUP.md) for configuration guide

### Potential Future Enhancements

- Enable OpenAI GPT models (currently commented due to rate limits)
  - Uncomment integration code in agent files when API limits resolved
  - GPT-4o-mini for clarity and validation
  - GPT-4o for natural language synthesis
- Persistent database for conversation history (currently in-memory only)
- Expand business domain coverage beyond current 15 sources (configured in config.py)
- Financial data APIs (real-time stock prices, earnings data)
- Web UI with Streamlit or Gradio
- Unit tests with pytest and integration test suite
- Logging and monitoring with LangSmith
- Caching layer for frequent queries (reduce API costs)
- Rate limiting and retry with exponential backoff