# =============================================================================
# CONFIGURATION - Toggle between modes for testing and production
# =============================================================================

# RESEARCH MODE CONFIGURATION
# Set to True to enable strict validation (confidence must be 8+ to pass)
# Set to False for normal validation (confidence 6+ passes)
STRICT_VALIDATION_MODE = True  # Toggle: True = Strict (8+ threshold), False = Normal (6+ threshold)

# TAVILY CONFIGURATION
# Focus search on business/company news domains
TAVILY_SEARCH_DOMAINS = [
    "bloomberg.com",
    "reuters.com",
    "cnbc.com",
    "wsj.com",
    "ft.com",
    "forbes.com",
    "businessinsider.com",
    "marketwatch.com",
    "finance.yahoo.com",
    "seekingalpha.com",
    "fool.com",
    "benzinga.com",
    "thestreet.com",
    "investing.com",
    "barrons.com"
]

# VALIDATION THRESHOLDS
# In strict mode, require higher confidence to pass validation
STRICT_CONFIDENCE_THRESHOLD = 8  # Must have 8+ confidence in strict mode
NORMAL_CONFIDENCE_THRESHOLD = 6  # 6+ confidence in normal mode

# MINIMUM ANSWER LENGTH
# Reject answers that are too short (likely irrelevant)
MIN_ANSWER_LENGTH = 50  # characters

# COMPANY-RELATED KEYWORDS
# Check if results actually contain company-related content
COMPANY_KEYWORDS = [
    "stock", "shares", "trading", "market", "ceo", "company", "corporation",
    "revenue", "earnings", "profit", "loss", "quarterly", "annual", "investors",
    "nasdaq", "nyse", "ipo", "acquisition", "merger", "business", "industry"
]
