"""
THIS STAGE 06 TAKES THE FILTERED SEMANTIC RESULTS FROM STAGE 05 AS INPUT AND ASSEMBLES THEM INTO THE EXACT STRUCTURE REQUIRED:
| SOURCE DOMAIN | TARGET URL | DETECTED KEYWORD | RELEVANCE SCORE |

THE FOLLOWING HELPER FUNCTIONS ARE NEEDED TO ACHIEVE THE TASK FOR THIS STAGE:
FUNCTION TO VALIDATE THE SEMANTIC RESULTS
FUNCTION TO FORMAT THE COLUMNS
FUNCTION TO SORT AND RANK THE RESULTS
FINAL ORCHESTRATOR TO ASSEMBLE THE OUTPUT - DATAFRAME
"""

import pandas as pd

# -------------------------------------------------
# VALIDATE SEMANTIC RESULTS - A DATAFRAME
# ------------------------------------------------
def validate_semantic_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    THIS FUNCTION VALIDATES THAT THE SEMANTIC FILTERING OUTPUT HAS THE REQUIRED COLUMNS AND THAT IT IS CLEAN.
    """
    required_columns = ["Source Domain", "Target URL", "Detected Keyword", "Relevance Score"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # REMOVE ROWS WITH MISSING URLs OR DOMAINS
    df = df.dropna(subset=["Source Domain", "Target URL"])

    return df


# ------------------------------------------
# FORMAT OUTPUT COLUMNS - DATAFRAME
# -----------------------------------------
def format_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    THIS FUNCTION FORMATS COLUMNS TO ENSURE CONSISTENCY AND CLEANLINESS.
    """
    df["Source Domain"] = df["Source Domain"].str.strip().str.lower()
    df["Target URL"] = df["Target URL"].str.strip()
    df["Detected Keyword"] = df["Detected Keyword"].fillna("N/A")
    df["Relevance Score"] = df["Relevance Score"].astype(float).round(4)

    return df


# ----------------------------------
# RANKING RESULTS - DATAFRAME
# ----------------------------------
def rank_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    THIS FUNCTION SORTS RESULTS BY RELEVANCE SCORE IN DESCENDING ORDER.
    """
    return df.sort_values(by="Relevance Score", ascending=False).reset_index(drop=True)


# ----------------------------------------------------------------
# ASSEMBLING THE OUTPUT ORCHESTRATOR - DATAFRAME
# ----------------------------------------------------------------
def assemble_spreadsheet_csv_output(semantic_df: pd.DataFrame) -> pd.DataFrame:
    """
    THIS FUNCTION BUILDS THE FINAL SPREADSHEET-READY DATAFRAME FROM SEMANTIC FILTERING RESULTS.
    """

    # STEP 1 - VALIDATE SEMANTIC RESULTS
    validated = validate_semantic_results(semantic_df)

    # STEP 2 - FORMAT OUTPUT COLUMNS
    formatted = format_output_columns(validated)

    # STEP 3 - RANK RESULTS
    ranked = rank_results(formatted)

    return ranked