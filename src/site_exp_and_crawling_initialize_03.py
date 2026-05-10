
"""
STAGE 03 - HERE THE PROJECT STOPS BEING JUST CSV AND BECOME ACTUAL CRAWLER.
WE ARE INTERESTED IN SYSTEMATICALLY START EXPLORING THE INTERNAL PAGES OF
THE VALIDATED DOMAINS OBTAINED FROM PREVIOUS STAGES - 02.

HERE, THE GOAL IS TO:
DEFINE HOW CRAWLING WILL BEHAVE - STRATEGY, LIMITS AND POLITENESS
BUILD THE INITIAL CRAWL QUEUE - STARTING URLS AND METADATA
ATTACH PRIORITIES SO THE CRAWLER EXPLORES THE MOST PROMISING SITES OR URLs FIRST.

THE INPUT FOR STAGE 3 IS/ARE THE OUTPUTS FROM STAGE 02 - DATAFRAME AND OPTIONALLY CLEANED KEYWORDS FROM STAGE 01 TO HELP PRIORITIZE.

THE OUTPUT IS A CRAWL QUEUE: A STRUCTURE LIST/DATAFRAME OF URLs TO VISIT WITH METADATA.

FOR MAINTAINABILITY AND REPRODUCIBILITY, A CONFIGURATION FILE IS SET TO HOLDS THE PARAMTERS THAT CONTROLS THE CRAWLER BEHAVIOUR -
MAX_DEPTH, MAX_PAGES_PER_DOMAIN, SAME_DOMAIN_ONLY, POLITE_DELAY, TIMEOUT, USER_AGENT.
"""

import pandas as pd
from src.config import PRIORITY_WEIGHTS, MAX_CRAWL_DEPTH, MAX_PAGES_PER_DOMAIN

# -------------------------------------------------------------
# BUILD THE HOMEPAGE URL
# -------------------------------------------------------------
def build_homepage_url(domain: str) -> str:
    """
    CONSTRUCTS A STANDARDIZED HTTPS HOMEPAGE URL FOR A DOMAIN.
    """
    domain = domain.strip().lower()
    return f"https://{domain}/"


# --------------------------------------------------------------
# COMPUTE PRIORITY SCORE
# --------------------------------------------------------------
# def compute_priority_score(homepage_title: str, homepage_h1: str, internal_links: int, keywords: list) -> float:
#     """
#     COMPUTES A PRIORITY SCORE FOR THE DOMAIN BASED ON HOMEPAGE SIGNALS
#     """
#     score = 1.0

#     # KEYWORD MATCHING IN THE TITLE
#     if homepage_title:
#         if any(title in homepage_title.lower() for title in keywords):
#             score += PRIORITY_WEIGHTS["keyword_title_bonus"]

#     # KEYWORD MATCHING IN H1
#     if homepage_h1:
#         if any(tag in homepage_h1.lower() for tag in keywords):
#             score += PRIORITY_WEIGHTS["keyword_h1_bonus"]

#     # INTERNAL LINK RICHNESS
#     if internal_links > 30:
#         score += PRIORITY_WEIGHTS["internal_links_high"]
#     elif internal_links > 10:
#         score += PRIORITY_WEIGHTS["internal_links_medium"]

#     return score

def compute_priority_score(homepage_title: str, homepage_h1: str, internal_links: int, keywords: list) -> float:
    """
    COMPUTES A PRIORITY SCORE FOR THE DOMAIN BASED ON HOMEPAGE SIGNALS.
    SAFELY HANDLES None, NaN, EMPTY STRINGS, AND MIXED CASE.
    """

    # Base score
    score = 1.0

    # --- SAFELY NORMALIZE TITLE ---
    if homepage_title is None:
        homepage_title = ""
    homepage_title = str(homepage_title).lower()

    # --- SAFELY NORMALIZE H1 ---
    if homepage_h1 is None:
        homepage_h1 = ""
    homepage_h1 = str(homepage_h1).lower()

    # --- SAFELY NORMALIZE KEYWORDS ---
    keywords = [str(kw).lower().strip() for kw in keywords if kw]

    # --- KEYWORD MATCHING IN TITLE ---
    if any(kw in homepage_title for kw in keywords):
        score += PRIORITY_WEIGHTS["keyword_title_bonus"]

    # --- KEYWORD MATCHING IN H1 ---
    if any(kw in homepage_h1 for kw in keywords):
        score += PRIORITY_WEIGHTS["keyword_h1_bonus"]

    # --- INTERNAL LINK RICHNESS ---
    if internal_links > 30:
        score += PRIORITY_WEIGHTS["internal_links_high"]
    elif internal_links > 10:
        score += PRIORITY_WEIGHTS["internal_links_medium"]

    return score

# --------------------------------------------------------------------------
# CREATE QUERY ENTRY
# --------------------------------------------------------------------------
def create_queue_entry(url: str, domain: str, depth: int, priority: float, source: str) -> dict:
    """
    CREATES A STANDARDIZED QUEUE ENTRY FOR THE CRAWLER.
    """
    return {
        "url": url,
        "domain": domain,
        "depth": depth,
        "priority": priority,
        "source": source,
        "status": "pending"
    }


# ------------------------------------------------------------------------
# INITIALIZE ALREADY SEEN URL - URL SET
# ------------------------------------------------------------------------
def initialize_seen_set() -> set:
    """
    INITIALIZES THE SET USED TO TRACK ALREADY-ADDED URLS.
    """
    return set()


# -----------------------------------------------------------------------
# ADD URL TO QUEUE WITH DUPLICATE PROTECTION
# -----------------------------------------------------------------------
def add_to_queue(queue: list, already_seen: set, entry: dict):
    """
    ADDS A NEW URL ENTRY TO THE QUEUE IF NOT ALREADY SEEN.
    """
    url = entry["url"]
    if url not in already_seen:
        queue.append(entry)
        already_seen.add(url)                        


# ----------------------------------------------------------------------
# ORCHESTRATOR SCRIPTS FOR INITIALIZING THE CRAWL QUEUE
# ----------------------------------------------------------------------
def initialize_crawl_queue(domains_df: pd.DataFrame, keywords_df: pd.DataFrame) -> pd.DataFrame:
    """
    BUILDS THE INITIAL CRAWL QUEUE USING THE CONFIGURATION SETTINGS FROM THE PREPROCESSED DOMAINS.
    EACH DOMAIN CONTRIBUTES ITS HOMEPAGE AS A SEED URL.
    """

    keywords = keywords_df["keyword"].tolist()

    queue = []
    already_seen = initialize_seen_set()

    for _, row in domains_df.iterrows():
        domain = row["domain"]
        homepage_url = row.get("homepage_url", build_homepage_url(domain))

        # COMPUTE PRIORITY USING CONFIG WEIGHTS
        priority = compute_priority_score(
            homepage_title=row.get("homepage_title"),
            homepage_h1=row.get("homepage_h1"),
            internal_links=row.get("internal_links", 0),
            keywords=keywords
        )

        # CREATE QUEUE ENTRY
        entry = create_queue_entry(
            url=homepage_url,
            domain=domain,
            depth=0,
            priority=priority,
            source="seed"
        )

        # ADD TO QUEUE WITH DUPLICATE PROTECTION
        add_to_queue(queue, already_seen, entry)

    # CONVERT TO DATAFRAME
    queue_df = pd.DataFrame(queue)

    # ATTACH CONFIGURATION VALUES FOR DOWNSTREAM STAGES
    queue_df["max_depth"] = MAX_CRAWL_DEPTH
    queue_df["max_pages_per_domain"] = MAX_PAGES_PER_DOMAIN

    return queue_df
