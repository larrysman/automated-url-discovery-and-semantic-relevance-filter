# UTILITY HELPER FUNCTIONS
from urllib.parse import urlparse
import re
import os
from config.config import UTILITY_CONFIG


# NORMALIZING THE DOMAIN NAMES 
def domain_name_normalization(domain: str) -> str:
    """
    THE FUNCTION NORMALIZES THE DOMAIN NAME BY REMOVING TRAILING WHITESPACES, ADDING PROTOCOLS (HTTPS) IF MISSING
    AND ENSURING SHEME AND STRIP TRAILING SLASHES.

    Args:
        domain | str: THE DOMAIN NAME TO BE NORMALIZED.

    Returns:
        normalized_domain | str: THE NORMALIZED DOMAIN NAME.
    """

    # STRIP TRAILING WHITESPACES
    if not domain:
        return domain.strip()
    #domain = domain.strip()

    # ADD PROTOCOL (HTTPS) IF MISSING
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"

    return domain.rstrip('/')


# EXTRACT DOMAIN NAME FROM THE NORMALIZED DOMAIN_URL NAME
def extract_domain_from_url(url: str) -> str:
    """
    THE FUNCTION EXTRACTS THE DOMAIN NAME FROM THE NORMALIZED DOMAIN_URL NAME.
    Args:
        url | str: THE NORMALIZED DOMAIN_URL NAME.
        
    Returns:
        domain | str: THE EXTRACTED DOMAIN NAME.
    """
    url = domain_name_normalization(url)
    try:
        return urlparse(url).netloc
    except Exception as e:
        print(f"Error occurred while parsing URL: {e}")
        return url


# CHECK FOR UTILITY URL PAGES
def is_utility_url(url: str) -> bool:
    """
    THE FUNCTION CHECKS IF THE URL CONTAINS THE UTILITY PAGES AND RETURN TRUE IF IT CONTAINS
    THE UTILITY PAGES OTHERWISE IS A FALSE.

    Args:
        url | str: TAKES THE NORMALIZED URLS

    Returns:
        True if the url contains the utility pages otherwise is False.
    """
    normalized_url = domain_name_normalization(url)

    # EXTRACT ONLY THE PATH
    PATH = urlparse(normalized_url).path.lower()
    
    UTILITY_PATTERNS = UTILITY_CONFIG
    for utility_page in UTILITY_PATTERNS:
        if re.search(utility_page, PATH):
            return True
    return False

# CHECKS IF THE UTILITY LOOKS LIKE THE UTILITY TITLE
def looks_like_utility_title(title: str) -> bool:
    """
    THE FUNCTION DETECT THAT THE UTILITY LIKE TITLES

    Args:
        title | str: TAKES THE PAGE TITLE

    Returns:
        True if the UTILITY TITLE is a part of UTILITY otherwise False
    """
    if not title:
        return False
    utility_title = title.lower()
    for suggested_title in ("about", "contact", "privacy", "terms", "login", "register", "subscribe"):
        if suggested_title in utility_title:
            return True
    return False

# REMOVING DUPLICATES AND PRESERVING ORDER
def remove_duplicate_and_preserve_order(items: list) -> list:
    previously_seen = set()
    output_list_without_duplicate = []
    for item in items:
        if item not in previously_seen:
            previously_seen.add(item)
            output_list_without_duplicate.append(item)
    return output_list_without_duplicate


# if __name__ == "__main__":
#     test_domains = [
#         "example.com",
#         "www.example.com",
#         "http://Example.coM/login",
#         "https://example.com",
#         "   example.com   ",
#         "example.com/terms",
#         "http://www.example.com/",
#         "https://www.example.com/",
#         ""
#     ]

#     for domain in test_domains:
#         normalized = is_utility_url(domain)
#         print(f"Original: '{domain}' -> Normalized: '{normalized}'")


