"""
THIS STAGE 05 DECIDES WHICH DISCOVERED URLs ARE ACTUALLY RELEVANT TO THE KEYWORDS.
A MODULARIZED IMPLEMENTATION FOR THIS STAGE INCLUDE:
LEXICAL RELEVANCE - KEYWORD MATCHING IN THE TITLE, H1, URLs SLUG, TEXT.
SEMANTIC RELEVANCE - USING THE TF-IDF AND COSINE SIMILARITY
CONFIGURATION THRESHOLDS - MIN_RELEVANCE_SCORE
UTILITY PAGE EXCLUSION - FURTHER REINFORCED AT THIS STAGE THOUGH COMPLETED IN STAGE 04.
"""

import pandas as pd
from bs4 import BeautifulSoup
from config import MAX_TEXT_LENGTH, MIN_RELEVANCE_SCORE
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------
# EXTRACTING PAGE VISIBLE TEXT FOR SCORING - HTML
# ---------------------------------------------------
def extract_page_text(html: str) -> str:
    """
    THIS FUNCTION EXTRACTS CLEAN VISIBLE TEXT FROM HTML FOR SEMANTIC SCORING.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # REMOVE SCRIPTS AND STYLE
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator=" ", strip=True)

    # LIMIT TEXT LENGTH
    return text[:MAX_TEXT_LENGTH]


# -------------------------------------------------------------
# LEXICAL MATCH SCORING FOR URL, TITLE, H1 AND KEYWORDS
# -------------------------------------------------------------
def lexical_match_score(url: str, title: str, h1: str, keywords: list) -> float:
    """
    THIS FUNCTION CHECKS FOR DIRECT KEYWORD MATCHES AND RETURNS A LEXICAL MATCH SCORE BASED ON KEYWORD PRESENCE IN URL, TITLE, OR H1.
    """
    score = 0.0
    url_l = url.lower()
    title_l = title.lower() if title else ""
    h1_l = h1.lower() if h1 else ""

    for kw in keywords:
        if kw in url_l:
            score += 0.4
        if kw in title_l:
            score += 0.4
        if kw in h1_l:
            score += 0.4

    return min(score, 1.0)

# -----------------------------------------
# SEMANTIC SIMILARITY FOR TEXT AND KEYWORDS
# -----------------------------------------
def semantic_similarity(text: str, keywords: list) -> float:
    """
    THIS FUNCTION COMPUTES SEMANTIC SIMILARITY BETWEEN PAGE TEXT AND KEYWORDS USING TF-IDF AND COSINE SIMILARITY.
    """
    if not text:
        return 0.0

    docs = [text] + keywords
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs)

    page_vec = tfidf[0:1]
    keyword_vecs = tfidf[1:]

    sims = cosine_similarity(page_vec, keyword_vecs)[0]
    return float(sims.max()) if len(sims) else 0.0


# ------------------------------------------------------
# COMPUTE RELEVANCE SCORE
# ------------------------------------------------------
def compute_relevance_score(lexical: float, semantic: float) -> float:
    """
    THIS FUNCTION COMBINES LEXICAL AND SEMANTIC SCORES INTO A FINAL RELEVANCE SCORE.
    """
    return round((0.4 * lexical) + (0.6 * semantic), 4)

# -------------------------------------------------------
# DETECTING TRIGGER KEYWORD
# -------------------------------------------------------
def detect_trigger_keyword(text: str, url: str, title: str, h1: str, keywords: list) -> str:
    """
    THIS FUNCTION IDENTIFIES WHICH KEYWORD TRIGGERED THE MATCH AND RETURNS THE FIRST KEYWORD THAT APPEARS IN URL, TITLE, H1, OR TEXT.
    """
    text_l = text.lower()
    url_l = url.lower()
    title_l = title.lower() if title else ""
    h1_l = h1.lower() if h1 else ""

    for kw in keywords:
        if kw in url_l or kw in title_l or kw in h1_l or kw in text_l:
            return kw

    return None

# -----------------------------------------------
# FILTERING BY RELEVANCE
# -----------------------------------------------
def filter_by_relevance(score: float) -> bool:
    """
    THIS FUNCTION USES THE CONFIG THRESHOLD FOR MIN_RELEVANCE_SCORE AND RETURNS TRUE IF THE PAGE PASSES THE MINIMUM RELEVANCE THRESHOLD.
    """
    return score >= MIN_RELEVANCE_SCORE


# ------------------------------------------------------------------------------------
# FINAL ORCHESTRATOR FOR SEMANTIC FILTERING FOR THE QUEUE DF AND INTEGRATE ALL STAGE 5
# ------------------------------------------------------------------------------------
def orchestrate_semantic_filtering(queue_df: pd.DataFrame, keywords_df: pd.DataFrame) -> pd.DataFrame:
    """
    RUNS SEMANTIC RELEVANCE FILTERING ON ALL CRAWLED PAGES.
    RETURNS ONLY RELEVANT PAGES WITH SCORES AND TRIGGER KEYWORDS.
    """

    keywords = keywords_df["keyword"].tolist()
    results = []

    for _, row in queue_df.iterrows():
        if row["status"] != "done":
            continue

        url = row["url"]
        html = row.get("html", None)
        title = row.get("title", None)
        h1 = row.get("h1", None)

        # EXTRACT THE TEXT
        text = extract_page_text(html)

        # LEXICAL SCORE
        lexical = lexical_match_score(url, title, h1, keywords)

        # SEMANTIC SCORE
        semantic = semantic_similarity(text, keywords)

        # FINAL RELEVANCE SCORE
        relevance = compute_relevance_score(lexical, semantic)

        # TRIGGER KEYWORD
        trigger = detect_trigger_keyword(text, url, title, h1, keywords)

        # FILTERING BY RELEVANCE
        if filter_by_relevance(relevance):
            results.append({
                "Source Domain": row["domain"],
                "Target URL": url,
                "Detected Keyword": trigger,
                "Relevance Score": relevance
            })

    return pd.DataFrame(results)





