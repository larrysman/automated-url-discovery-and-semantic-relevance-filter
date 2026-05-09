"""
GLOBAL CONFIGURATION FILE FOR THE AUTOMATED URL DISCOVERY PIPELINE.
ALL STAGES (LOADING, PREPROCESSING, CRAWLING, FILTERING) IMPORT FROM HERE.
"""

# ---------------------------------------------------------
# CRAWLER SETTINGS
# ---------------------------------------------------------

# Maximum depth to crawl (0 = homepage only, 1 = homepage + internal links)
MAX_CRAWL_DEPTH = 2

# Maximum number of pages to crawl per domain
MAX_PAGES_PER_DOMAIN = 50

# Delay between requests (politeness) in seconds
POLITE_DELAY = 0.5

# Request timeout in seconds
REQUEST_TIMEOUT = 8

# User-Agent header
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

# Only follow links within the same domain
SAME_DOMAIN_ONLY = True


# ---------------------------------------------------------
# SEMANTIC FILTERING SETTINGS
# ---------------------------------------------------------

# Minimum relevance score required to keep a page
MIN_RELEVANCE_SCORE = 0.35


# ---------------------------------------------------------
# UTILITY PAGE PATTERNS (TO EXCLUDE)
# ---------------------------------------------------------

UTILITY_PATTERNS = [
    "/about", "/contact", "/privacy", "/terms", "/login", "/signup",
    "/cookie", "/press", "/careers", "/subscribe", "/search", "/tag",
    "/sitemap", "/faq", "/help", "/support"
]


# ---------------------------------------------------------
# HTML PARSING SETTINGS
# ---------------------------------------------------------

# Maximum characters to extract from a page before chunking
MAX_TEXT_LENGTH = 20000


# ---------------------------------------------------------
# PRIORITY SCORING WEIGHTS
# ---------------------------------------------------------

PRIORITY_WEIGHTS = {
    "keyword_title_bonus": 1.0,
    "keyword_h1_bonus": 1.0,
    "internal_links_high": 0.5,
    "internal_links_medium": 0.2,
}
