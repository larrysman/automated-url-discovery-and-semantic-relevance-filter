"""
THIS STAGE 04 BUILT ON THE CONFIGURATION FILE AND DO THE FOLLOWING:
FETCHES PAGES
EXTRACT INTERNAL LINKS
NORMALIZES URL
FILTERS OUT JUNK AND UTILITY PAGES
EXPANDS THE CRAWL QUEUE
DISCOVERS DEEP URLS CONTAINING RELEVANT CONTENT.

INPUT: USES THE OUTPUT FROM STAGE 03
OUTPUT: RETURNS THE DATAFRAME
"""

import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from src.config import USER_AGENT, REQUEST_TIMEOUT, POLITE_DELAY, SAME_DOMAIN_ONLY, UTILITY_PATTERNS, MAX_CRAWL_DEPTH, MAX_PAGES_PER_DOMAIN


# -----------------------------------------
# FETCHING THE DOMAIN PAGE - URL
# -----------------------------------------
def fetch_page(url: str) -> tuple:
    """
    FETCHES A PAGE USING A POLITE, CONFIGURATION DRIVEN PROTOCOL (HTTP, HTTPS) REQUEST.
    RETURNS (HTML, STATUS_CODE) OR (None, None) ON FAILURE.
    """
    HEADERS = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        time.sleep(POLITE_DELAY)

        if response.status_code >= 400:
            return None, response.status_code

        return response.text, response.status_code

    except Exception:
        return None, None
    

# -------------------------------------------------------------------------
# EXTRACTING THE LINKS - HTML AND BASE_URL
# -------------------------------------------------------------------------
# def extract_links(html: str, base_url: str) -> list:
#     """
#     EXTRACTS ALL LINKS FROM A PAGE AND RETURNS ABSOLUTE URLS.
#     IT EXTRACTS ALL <a href=""> LINKS AND RESOLVES RELATIVES URLs
#     """
#     if not html:
#         return []

#     soup = BeautifulSoup(html, "html.parser")
#     links = []

#     for tag in soup.find_all("a", href=True):
#         href = tag["href"].strip()
#         absolute = urljoin(base_url, href)
#         links.append(absolute)

#     return links

def extract_links(html: str, base_url: str) -> list:
    """
    EXTRACTS ALL VALID, CRAWLABLE LINKS FROM A PAGE.
    - Resolves relative URLs
    - Removes empty, fragment, mailto, tel, javascript links
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        # Skip empty hrefs
        if not href:
            continue

        # Skip fragments (#, #section)
        if href.startswith("#"):
            continue

        # Skip javascript links
        if href.lower().startswith("javascript:"):
            continue

        # Skip mailto and tel links
        if href.lower().startswith(("mailto:", "tel:")):
            continue

        # Convert to absolute URL
        absolute = urljoin(base_url, href)
        links.append(absolute)

    return links


# --------------------------------------------------------------
# NORMALIZING THE URL - REMOVING FRAGMENTS, TRAILING SLASHES ETC
# --------------------------------------------------------------
def normalize_url(url: str) -> str:
    """
    NORMALIZES URL BY REMOVING FRAGMENTS AND TRAILING SLASHES.
    """
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="")
    normalized = urlunparse(cleaned).rstrip("/")
    return normalized


# -----------------------------------------------------------------------
# FILTERING LINKS BY DOMIAN - LINKS, DOMAIN USING SAME_DOMAIN_ONLY CONFIG
# -----------------------------------------------------------------------
def filter_links_by_domain(links: list, domain: str) -> list:
    """
    KEEPS ONLY LINKS THAT BELONG TO THE SAME DOMAIN (IF ENABLED).
    """
    if not SAME_DOMAIN_ONLY:
        return links

    filtered = []
    for link in links:
        try:
            if urlparse(link).netloc == domain:
                filtered.append(link)
        except:
            continue

    return filtered


# ------------------------------------------------------------
# FILTERING THE UTILITY PAGES - LINKS USING THE UTILITY_CONFIG
# ------------------------------------------------------------
def filter_utility_pages(links: list) -> list:
    """
    THIS FUNCTION REMOVES UTILITY PAGES LIKE /about, /contact, /privacy, ETC.
    """
    cleaned = []
    for link in links:
        if not any(pattern in link.lower() for pattern in UTILITY_PATTERNS):
            cleaned.append(link)
    return cleaned


# --------------------------------------------------
# CREATE CHILD AND QUEUE ENTRIES FOR DISCOVERED URLs
# --------------------------------------------------
def create_child_queue_entries(parent_entry: dict, child_urls: list) -> list:
    """
    THE FUNCTION CREATES NEW QUEUE ENTRIES FOR CHILD URLS WITH DEPTH + 1.
    """
    new_entries = []
    for url in child_urls:
        new_entries.append({
            "url": url,
            "domain": parent_entry["domain"],
            "depth": parent_entry["depth"] + 1,
            # INHERIT PRIORITY
            "priority": parent_entry["priority"],
            "source": "internal_link",
            "status": "pending"
        })
    return new_entries


# -------------------------------------------------------------------------
# ENFORCING THE CRAWLING LIMITS USING MAX_CRAWL_DEPTH, MAX_PAGES_PER_DOMAIN
# -------------------------------------------------------------------------
def enforce_crawl_limits(entry: dict, domain_page_count: int) -> bool:
    """
    RETURNS TRUE IF THE ENTRY SHOULD BE CRAWLED, FALSE IF LIMITS ARE EXCEEDED.
    """
    if entry["depth"] > MAX_CRAWL_DEPTH:
        return False

    if domain_page_count >= MAX_PAGES_PER_DOMAIN:
        return False

    return True


# -------------------------------------------------------------------------------
# ORCHESTRATOR SCRIPTS FOR THE CRAWL - INTEGRATED ALL MODULES IN STAGE 4 TOGETHER
# -------------------------------------------------------------------------------
def orchestrate_crawl_query(queue_df: pd.DataFrame) -> pd.DataFrame:
    """
    MAIN CRAWLING LOOP: FETCHES PAGES, EXTRACTS LINKS, EXPANDS QUEUE AND RETURNS AN UPDATED QUEUE WITH DISCOVERED URLS.
    """

    queue = queue_df.to_dict("records")
    already_seen = set([entry["url"] for entry in queue])
    domain_page_count = {}

    i = 0
    while i < len(queue):
        entry = queue[i]
        domain = entry["domain"]

        # INITIALIZE DOMAIN COUNT
        domain_page_count.setdefault(domain, 0)

        # ENFORCE CRAWL LIMITS
        if not enforce_crawl_limits(entry, domain_page_count[domain]):
            entry["status"] = "skipped"
            i += 1
            continue

        # FETCHING PAGE
        html, status_code = fetch_page(entry["url"])
        entry["status"] = "done" if html else "failed"
        domain_page_count[domain] += 1

        if not html:
            i += 1
            continue

        # EXTRACT AND PROCESS LINKS
        links = extract_links(html, entry["url"])
        links = [normalize_url(link) for link in links]
        links = filter_links_by_domain(links, domain)
        links = filter_utility_pages(links)

        # CREATE CHILD ENTRIES
        children = create_child_queue_entries(entry, links)

        # ADD NEW ENTRIES TO QUEUE
        for child in children:
            if child["url"] not in already_seen:
                queue.append(child)
                already_seen.add(child["url"])

        i += 1

    return pd.DataFrame(queue)
