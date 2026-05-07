# LOAD THE INPUT DOMAINS DATA AND TARGET KEYWORD DATA

import numpy as np
import pandas as pd
import os
from typing import Tuple

def loading_data(input_domains_path: str, target_keywords_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    THE FUNCTION LOADS THE INPUT DOMAINS AND TARGET KEYWORDS DATA FROM THE GIVEN PATHS AND RETURNS THEM AS PANDAS DATAFRAMES.

    Args:
        input_domains_path | str: THE PATH TO THE INPUT DOMAINS CSV FILE.
        target_keywords_path | str: THE PATH TO THE TARGET KEYWORDS CSV FILE.

    Returns:
        input_domains_df | pd.DataFrame: THE LOADED INPUT DOMAINS DATA AS A PANDAS DATAFRAME.
        target_keywords_df | pd.DataFrame: THE LOADED TARGET KEYWORDS DATA AS A PANDAS DATAFRAME.
    """

    # LOAD THE INPUT DOMAINS DATA
    input_domains_df = pd.read_csv(input_domains_path)

    # LOAD THE TARGET KEYWORDS DATA
    target_keywords_df = pd.read_csv(target_keywords_path)

    return input_domains_df, target_keywords_df


if __name__ == "__main__":
    input_domains_path = "./data/input_domains.csv"
    target_keywords_path = "./data/target_keywords.csv"

    input_domains_df, target_keywords_df = loading_data(input_domains_path, target_keywords_path)

    print("INPUT DOMAINS DATA:")
    print(input_domains_df.head())

    print("\nTARGET KEYWORDS DATA:")
    print(target_keywords_df.head())

