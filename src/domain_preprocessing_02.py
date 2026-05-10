# STAGE 02 - DOMAIN PRE-PROCESSING - DEEP EXPLORATION
"""
TAKES CLEANED INPUT FROM STAGE 01 AND PREPARES IT FOR CRAWLING
TURN A LIST OF NORMALIZED DOMAINS INTO STRUCTURED, VALIDATED, CRAWL-READY DATAFRAME.

THIS STAGE IS THE BRIDGE BETWEEN RAW CSV INOUT AND A CRAWLER-READY DOMAIN LIST.
"""

import requests
from bs4 import BeautifulSoup
from typing import Tuple
import pandas as pd

def preprocessing_domains(domains_df: pd.DataFrame) -> pd.DataFrame:
    """
    PERFORMS DOMAIN PRE-PROCESSING TO PREPARE FOR CRAWLING.
    INCLUDES CANONICALIZATION (THE FINAL NORMALIZATION PASS), HEALTH CHECKS (CRITICAL FILTERING),
    AND HOMEPAGE FETCH AND METADATA EXTRACTION.

    Args:
        domains_df | pd.DataFrame: CLEANED DOMAINS FROM STAGE 1.

    Returns:
        pd.DataFrame: CRAWL-READY DOMAIN DATAFRAME WITH METADATA.
    """

    def canonicalize_for_final_normalization(domain: str) -> str:
        domain = domain.strip().lower()
        return domain

    # FETCH THE HOMEPAGE BASED ON THE INPUT DOMAIN
    def fetch_the_homepage(domain: str):
        url = f"https://{domain}"
        try:
            response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code >= 400:
                return None, None, None, None, "bad_status"
            return url, response.text, response.status_code, response.headers, "ok"
        except Exception:
            return None, None, None, None, "error"

    # EXTRACT TAGS FOR TITLE, H1 AND INTERNAL LINKS
    def extract_metadata_from_homepage(html: str):
        if not html:
            return None, None, 0

        soup = BeautifulSoup(html, "html.parser")

        # THE SEO TITLE OF THE PAGE
        # title = soup.title.string.strip() if soup.title else None
        title = soup.title.get_text(strip=True) if soup.title else None
        
        # THE MAIN HEADING OF THE PAGE
        h1_tag = soup.find("h1")
        h1 = h1_tag.get_text(strip=True) if h1_tag else None

        # ITERATE OVER THE PAGE FOR HYPERTEXT REFRENCE (HREF)
        internal_links = len([
            tag["href"] for tag in soup.find_all("a", href=True)
            if tag["href"].startswith("/") or tag["href"].startswith("#")
        ])

        return title, h1, internal_links

    # PREPARE THE OUTPUT STRUCTURE FROM THE EXTRACTED METADATA FROM THE PAGE
    results = []

    for _, row in domains_df.iterrows():
        domain = canonicalize_for_final_normalization(row["domain"])

        homepage_url, html, status_code, headers, status = fetch_the_homepage(domain)

        if status != "ok":
            results.append({
                "domain": domain,
                "homepage_url": homepage_url,
                "status": status,
                "homepage_title": None,
                "homepage_h1": None,
                "internal_links": 0,
                "is_valid": False
            })
            continue

        title, h1, internal_links = extract_metadata_from_homepage(html)

        results.append({
            "domain": domain,
            "homepage_url": homepage_url,
            "status": "ok",
            "homepage_title": title,
            "homepage_h1": h1,
            "internal_links": internal_links,
            "is_valid": True
        })

    return pd.DataFrame(results)
