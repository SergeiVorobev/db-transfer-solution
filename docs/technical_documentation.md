
### Technical Documentation

```markdown
# Technical Documentation

## Overview

This document provides a detailed explanation of the solution for synchronizing data between DEV and PROD databases.

## Architecture

The solution is designed as follows:
- **DEV Database**: Holds data to be validated and potentially transferred to PROD.
- **PROD Database**: The target database where new and updated records are inserted.
- **Python Scripts**: A collection of scripts to handle database creation, data insertion, extraction, validation, and transfer.

## Data Flow

1. **Extract** records from the DEV database that are not present in the PROD database or have been updated.
2. **Insert** or **update** the corresponding records in the PROD database.

## Files and Scripts

- **create_databases_and_tables.py**: Python script to create the required tables in both DEV and PROD databases.
- **insert_sample_data.py**: Python script to insert sample data into the DEV and PROD databases.
- **extract_data_from_dev.py**: Python script to extract data from the DEV database.
- **validate_and_transfer.py**: Python script that validates and transfers the data to the PROD database.
- **data_transfer.py**: Python script that orchestrates the extraction, validation, and transfer of data from DEV to PROD.

## Configuration

- The `.env` file contains the connection details for the DEV and PROD databases. Ensure these are set correctly before running any scripts.
