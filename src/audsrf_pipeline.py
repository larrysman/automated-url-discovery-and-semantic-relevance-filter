"""
THIS IS THE CHAINED PIPELINE FOR ALL THE STAGES 01 - 08 AND RUN THE PIPELINE END-TO-END IN A SINGLE RUNNABLE SCRIPT

`audsrf_pipeline.py` -> automated url discovery and semantic relevance filter pipeline.py
"""

import pandas as pd

# ------- STAGE 01 -----------
from src.load_and_clean_data_01 import load_and_normalize_data

# -------- STAGE 02 ----------
from src.domain_preprocessing_02 import preprocessing_domains

# -------- STAGE 03 ----------
from src.site_exp_and_crawling_initialize_03 import initialize_crawl_queue

# --------- STAGE 04 ---------
from src.crawling_and_deep_url_discovery_04 import orchestrate_crawl_query

# --------- STAGE 05 ---------
from src.semantic_relevance_filtering_05 import orchestrate_semantic_filtering

# --------- STAGE 06 --------
from src.assembling_output_06 import assemble_spreadsheet_csv_output

# --------- STAGE 07 --------
from src.final_csv_output_generation_07 import orchestrate_csv_export

# --------- STAGE 08 --------
from src.quality_checks_and_success_metrics_08 import orchestrate_quality_checks


def run_full_pipeline(
    input_domains_path: str,
    target_keywords_path: str,
    output_folder: str = "output"
) -> None:
    """
    THIS FUNCTION RUNS THE FULL PIPELINE OF ALL THE STAGES FROM 01 - 08 END-TO-END.
    """

    # -----------------------------
    # STAGE 1: LOAD AND NORMALIZE
    # -----------------------------
    domains_df, keywords_df, diagnostics = load_and_normalize_data(
        input_domains_path,
        target_keywords_path
    )
    print("STAGE 01 - LOAD AND NORMALIZE WITH DIAGNOSTICS SUMMARY:")
    print(diagnostics)

    # ------------------------------
    # STAGE 2: DOMAIN PRE-PROCESSING
    # ------------------------------
    preprocessed_domains_df = preprocessing_domains(domains_df)
    print(f"STAGE 02 - PREPROCESSING THE DOMAINS: {len(preprocessed_domains_df)}")

    # ---------------------------------------------------------
    # STAGE 3: SITE EXPANSION AND CRAWLING INITIALIZATION QUEUE
    # ---------------------------------------------------------
    initial_queue_df = initialize_crawl_queue(preprocessed_domains_df, keywords_df)
    print(f"STAGE 03 - INITIAL QUEUE SIZE: {len(initial_queue_df)}")

    # -----------------------------------------
    # STAGE 4: CRAWLING AND DEEP URL DISCOVERY
    # -----------------------------------------
    crawled_queue_df = orchestrate_crawl_query(initial_queue_df)
    print(f"STAGE 04 - TOTAL URLs DISCOVERED: {len(crawled_queue_df)}")

    # --------------------------------------------------------
    # STAGE 5: SEMANTIC RELEVANCE FILTERING
    # (ASSUMES crawled_queue_df CONTAINS html/title/h1 FIELDS)
    # ---------------------------------------------------------
    semantic_df = orchestrate_semantic_filtering(crawled_queue_df, keywords_df)
    print(f"STAGE 05 - RELEVANT URLs AFTER SEMANTIC FILTERING: {len(semantic_df)}")

    # ---------------------------------------------------------
    # STAGE 6: ASSEMBLYING OUTPUT - SPREADSHEET OUTPUT ASSEMBLY
    # ---------------------------------------------------------
    final_df = assemble_spreadsheet_csv_output(semantic_df)
    print(f"STAGE 06 - FINAL CSV AND SPREADSHEET ROWS: {len(final_df)}")

    # -----------------------------------------------
    # STAGE 7: FINAL CSV OUTPUT GENERATION AND EXPORT
    # -----------------------------------------------
    csv_path = orchestrate_csv_export(final_df, output_folder=output_folder)
    print(f"STAGE 07 - CSV exported to: {csv_path}")

    # -------------------------------------------
    # STAGE 8: QUALITY CHECKS AND SUCCESS METRICS
    # -------------------------------------------
    quality_report = orchestrate_quality_checks(final_df)
    print("STAGE 08 - QUALITY REPORT:")
    for key, value in quality_report.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    INPUT_DOMAINS_CSV = "./data/input_domains.csv"
    TARGET_KEYWORDS_CSV = "./data/target_keywords.csv"
    OUTPUT_FOLDER = "output"

    run_full_pipeline(
        input_domains_path=INPUT_DOMAINS_CSV,
        target_keywords_path=TARGET_KEYWORDS_CSV,
        output_folder=OUTPUT_FOLDER
    )
