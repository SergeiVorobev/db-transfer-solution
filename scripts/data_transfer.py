"""
# data_transfer.py

## Purpose:
This script orchestrates the data transfer process by:
1. Extracting data from the DEV database.
2. Validating and transferring data to the PROD database.
3. Optionally, it can also include logging or reporting.

## Usage:
    python3 scripts/data_transfer.py
"""

import logging
import os
import datetime
from dotenv import load_dotenv
from extract_data_from_dev import extract_new_records
from validate_and_transfer import validate_and_transfer_data

# Load environment variables
load_dotenv()


def main():
    try:
        logging.info("Starting data transfer process.")

        # Extract data from DEV database
        logging.info("Extracting data from DEV database.")
        data = extract_new_records()
        if not data:
            logging.info("No new records to transfer.")
            return
        
        logging.info(f"Extracted {len(data)} records from DEV database.")

        # Transfer data to PROD database
        logging.info("Validating and transferring data to PROD database.")
        validate_and_transfer_data()
        logging.info("Data transfer completed successfully.")
    
    except Exception as e:
        logging.error(f"Error during data transfer: {e}")

if __name__ == "__main__":
    main()
