# LOAD THE INPUT DOMAINS DATA AND TARGET KEYWORD DATA

import numpy as np
import pandas as pd
import os
from typing import Tuple, Dict
import re


def load_and_normalize_data(
        input_domains_path: str,
        target_keywords_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    THIS FUNCTION LOADS, VALIDATES, CLEANS, AND NORMALIZES THE INPUT DOMAINS AND TARGET KEYWORDS.

    Args:
        input_domains_path | str: PATH TO THE INPUT DOMAINS CSV FILE.
        target_keywords_path | str: PATH TO THE TARGET KEYWORDS CSV FILE.

    Returns:
        cleaned_domains_df | pd.DataFrame: CLEANED AND NORMALIZED DOMAINS
        cleaned_keywords_df | pd.DataFrame: CLEANED KEYWORDS.
        diagnostics | Dict: SUMMARY OF ISSUES FOUND DURING CLEANING
    """
    # -----------------------------------------------------
    # LOADING THE INPUT RAW DATA - DOMAINS AND KEYWORDS
    # -----------------------------------------------------
    domains_df = pd.read_csv(input_domains_path)
    keywords_df = pd.read_csv(target_keywords_path)

    diagnostics_check = {
        "initial_domain_count": len(domains_df),
        "initial_keyword_count": len(keywords_df),
        "removed_invalid_domains": 0,
        "removed_empty_keywords": 0,
        "duplicates_removed_domains": 0,
        "duplicates_removed_keywords": 0
    }

    # -------------------------------------------------------------------------
    # VALIDATING REQUIRED COLUMNS FOR THE INPUT RAW DATA - DOMAINS AND KEYWORDS
    # -------------------------------------------------------------------------
    if domains_df.shape[1] != 1:
        raise ValueError("input domains data must contain exactly ONE column.")
    
    if keywords_df.shape[1] != 1:
        raise ValueError("input keywords data must contain exactly ONE column.")
    
    # RENAMING THE DATASETS COLUMNS
    domains_df.columns = ["domain"]
    keywords_df.columns = ["keyword"]

    # ------------------------------------
    # CLEAN AND NORMALIZE THE DOMAINS CSV
    # ------------------------------------
    def normalize_domains_df(domain: str) -> str:
        if not isinstance(domain, str):
            return None
        
        domain = domain.strip().lower()

        # REMOVE EXISTING PROTOCOLS IN THE DOMAIN
        domain = re.sub(r"^https?://", "", domain)

        # REMOVE EXISTING WWW. IN THE DOMAIN
        domain = re.sub(r"^www\.", "", domain)

        # REMOVE PATHS AND QUERY PARAMETERS FROM DOMAIN
        domain = domain.split("/")[0]
        domain = domain.split("?")[0]

        # REMOVING TRAILING DOTS OR SLASHES FROM DOMAIN
        domain = domain.rstrip("/").rstrip(".")

        return domain if domain else None
    # APPLIED THE NORMALIZED DOMAINS DF TO THE DOMAINS_DF AND CREATED A NEW COLUMN CALLED NORMALIZED
    domains_df["normalized"] = domains_df["domain"].apply(normalize_domains_df)

    # DETECT MALFORMED DOMAINS
    def _is_valid_domain(domain: str) -> bool:
        if not isinstance(domain, str):
            return False
        if " " in domain:
            return False
        if "." not in domain:
            return False
        return True
    
    domains_df["valid"] = domains_df["normalized"].apply(_is_valid_domain)

    diagnostics_check["removed_invalid_domains"] = len(domains_df[~domains_df["valid"]])

    # KEEP ONLY VALID DOMAINS
    cleaned_domains_df = domains_df[domains_df["valid"]].copy()

    # REMOVING DUPLICATES
    before = len(cleaned_domains_df)
    cleaned_domains_df = cleaned_domains_df.drop_duplicates(subset=["normalized"])
    diagnostics_check["duplicates_removed_domains"] = before - len(cleaned_domains_df)

    cleaned_domains_df = cleaned_domains_df[["normalized"]].rename(columns={"normalized": "domain"})
    
    # ----------------------------
    # CLEAN AND NORMALIZE KEYWORDS
    # ----------------------------
    def clean_keywords_df(keyword: str) -> str:
        if not isinstance(keyword, str):
            return None
        
        keyword = keyword.strip().lower()
        return keyword if keyword else None
    
    keywords_df["cleaned"] = keywords_df["keyword"].apply(clean_keywords_df)

    # REMOVE EMPTY OR INVALID KEYWORDS
    diagnostics_check["removed_empty_keywords"] = len(keywords_df[keywords_df["cleaned"].isna()])

    cleaned_keywords_df = keywords_df[keywords_df["cleaned"].notna()].copy()

    # REMOVING DUPLICATES FOR THE KEYWORD DATASET
    before = len(cleaned_keywords_df)
    cleaned_keywords_df = cleaned_keywords_df.drop_duplicates(subset=["cleaned"])

    diagnostics_check["duplicates_removed_keywords"] = before - len(cleaned_keywords_df)

    cleaned_keywords_df = cleaned_keywords_df[["cleaned"]].rename(columns={"cleaned": "keyword"})

    # --------------------------------------------------
    # RETURN CLEANED DATA AND THE SUMMARIZED DIAGNOSTICS
    # --------------------------------------------------
    return cleaned_domains_df.reset_index(drop=True), cleaned_keywords_df.reset_index(drop=True), diagnostics_check

