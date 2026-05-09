"""
THE STAGE 07 TAKES THE ASSEMBLING_OUTPUT DATAFRAME FROM STAGE 06 AS INPUT AND SAVES IT INTO AN OUTPUT FOLDER IN CSV
AVAILABLE WITHIN THE PROJECT FOLDER STRUCTURE.
THE FOLLOWING HELPER FUNCTIONS ARE REQUIRED:
CREATE AN OUTPUT DIRECTORY IF IT DOES NOT EXIST
VALIDATE THE DATAFRAME BEFORE SAVING - ESSENTIAL FOR CONSISTENCY
SAVE CSV WITH A TIMESTAMP FILENAME
"""

import os
import pandas as pd
from datetime import datetime


# ---------------------------------------
# ENSURE OUTPUT FOLDER EXIST
# ---------------------------------------
def ensure_output_folder_exists(output_folder: str):
    """
    THIS FUNCTION CREATES THE OUTPUT FOLDER IF IT DOES NOT ALREADY EXIST.
    """
    os.makedirs(output_folder, exist_ok=True)


# ---------------------------------------
# VALIDATE OUTPUT DATAFRAME
# ---------------------------------------
def validate_output_dataframe(df: pd.DataFrame):
    """
    THIS FUNCTION VALIDATES THAT THE DATAFRAME IS NOT EMPTY AND HAS REQUIRED COLUMNS
    AND READY FOR EXPORT TO CSV.
    """
    if df is None or df.empty:
        raise ValueError("The output DataFrame is empty. Nothing to export.")

    required_columns = ["Source Domain", "Target URL", "Detected Keyword", "Relevance Score"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df


# -------------------------------------------
# GENERATE OUTPUT FILENAME
# -------------------------------------------
def generate_output_filename(prefix: str = "semantic_results") -> str:
    """
    THIS FUNCTION GENERATES A TIMESTAMPED CSV FILENAME WHICH ALLOWS FOR VERSIONING.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"


# --------------------------------------------
# SAVE DATAFRAME TO CSV
# --------------------------------------------
def save_dataframe_to_csv(df: pd.DataFrame, output_folder: str, filename: str) -> str:
    """
    THIS FUNCTION SAVES THE DATAFRAME TO A CSV FILE INSIDE THE OUTPUT FOLDER.
    RETURNS THE FULL PATH OF THE SAVED FILE.
    """
    full_path = os.path.join(output_folder, filename)
    df.to_csv(full_path, index=False)
    return full_path


# ------------------------------------------------------------------------------------
# ORCHESTRATOR FOR FINAL CSV GENERATION AND EXPORT - CHAINED ALL FUNCTIONS IN STAGE 07
# ------------------------------------------------------------------------------------
def orchestrate_csv_export(final_df: pd.DataFrame, output_folder: str = "output") -> str:
    """
    THIS FUNCTION ORCHESTRATES THE SPREADSHEET (CSV) EXPORT PROCESS:
    - VALIDATES DATAFRAME
    - CREATES OUTPUT FOLDER
    - GENERATES FILENAME
    - SAVES CSV
    RETURNS THE PATH TO THE SAVED FILE.
    """

    # STEP 1 - VALIDATE
    validated_df = validate_output_dataframe(final_df)

    # STEP 2 - ENSURE OUTPUT FOLDER EXISTS
    ensure_output_folder_exists(output_folder)

    # STEP 3 - GENERATE TIMESTAMPED FILENAME
    filename = generate_output_filename()

    # STEP 4 - SAVE CSV
    saved_path = save_dataframe_to_csv(validated_df, output_folder, filename)

    return saved_path




