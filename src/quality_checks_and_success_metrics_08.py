"""
THE STAGE 08 - QUALITY CHECKS AND SUCCESS METRICS IS THE FINAL INTELLIGENT LAYER THAT VALIDATES AND EVALUATE THE OUTPUTS,
DETECTING WEAKNESSES AND ENSURING THE FINAL CSV IS TRUTHWORTHY, PRECISE AND ACTIONABLE.

THE GOAL IS TO BE ABLE TO ANSWER THE FOLLOWING QUESTIONS:
DID THE SOLUTION EXCLUDE IRRELEVANT AND JUNK DOMAINS?
DID THE SOLUTION FIND DEEP URLs INSTEAD OF JUNK HOMEPAGES?
ARE THE RELEVANCE SCORES MEANINGFUL AND CONSISTENT?
"""


# ----------------------------
# CHECK PRECISION - DATAFRAME
# ----------------------------
def check_precision(df):
    """
    CALCULATES PRECISION METRIC:
    % OF URLs THAT ARE DEEP PAGES NOT HOMEPAGES.
    MEASURES HOW MANY URLs ARE ACTUALLY DEEP PAGES.

    MEANING: FOR EXAMPLE
    If precision = 0.85, then 85% of the output URLs are deep pages and this is excellent.
    """
    if df.empty:
        return 0.0

    deep_pages = df["Target URL"].apply(lambda x: "/" in x.rstrip("/")[len("https://"):])
    precision = deep_pages.mean()

    return round(float(precision), 4)


# ---------------------------------------------------------
# CHECK GRANULARITY - DATAFRAME
# ---------------------------------------------------------
def check_granularity(df):
    """
    THIS FUNCTION MEASURES HOW MANY UNIQUE DEEP URLs WERE DISCOVERED PER DOMAIN RETURNS A DICTIONARY:
    domain -> number of deep URLs discovered.

    MEANING:
    Which domains produced rich content vs shallow or no content.
    """
    granularity = {}

    for domain in df["Source Domain"].unique():
        subset = df[df["Source Domain"] == domain]
        granularity[domain] = len(subset)

    return granularity



# -------------------------------------------------------
# CHECK RELEVANCE DISTRIBUTION - DATAFRAME
# -------------------------------------------------------
def check_relevance_distribution(df):
    """
    THIS FUNCTIONS SHOWS HOW STRONG THE RELEVANCE SCORES ARE AND RETURNS BASIC STATISTICS ABOUT RELEVANCE SCORES.

    MEANING:
    if mean score is high, the semantic filtering is working well.
    """
    stats = {
        "min_score": float(df["Relevance Score"].min()),
        "max_score": float(df["Relevance Score"].max()),
        "mean_score": float(df["Relevance Score"].mean()),
        "median_score": float(df["Relevance Score"].median())
    }
    return stats


# -----------------------------------------------------------
# DETECT OFF TOPIC PAGES - DATAFRAME
# -----------------------------------------------------------
def detect_off_topic_pages(df):
    """
    THIS FUNCTION FLAGS SUSPICIOUS PAGES THAT PASSED THE FILTER BUT LOOK IRRELEVANT AND RETURNS A LIST OF URLs WITH LOW SCORES OR MISSING KEYWORDS.

    MEANING:
    Pages that might have slipped through the filter are flagged.
    """
    suspicious = df[
        (df["Relevance Score"] < 0.4) |
        (df["Detected Keyword"] == "N/A")
    ]

    return suspicious["Target URL"].tolist()


# ----------------------------------------------------------
# ORCHESTRATOR FOR QUALITY CHECKS AND SUCCESS METRICS
# ----------------------------------------------------------
def orchestrate_quality_checks(final_df):
    """
    THIS FUNCTION RUNS ALL QUALITY CHECKS AND RETURNS A SUMMARY REPORT.
    """

    report = {
        "precision": check_precision(final_df),
        "granularity": check_granularity(final_df),
        "relevance_distribution": check_relevance_distribution(final_df),
        "potential_off_topic_pages": detect_off_topic_pages(final_df)
    }

    return report






