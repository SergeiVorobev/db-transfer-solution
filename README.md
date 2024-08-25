# db-transfer-solution
## Database Sync Solution

This repository provides a complete solution for transferring and synchronizing data between DEV and PROD PostgreSQL databases. The solution includes Python scripts for creating databases, inserting sample data, and transferring data from DEV to PROD.

## Prerequisites
- PostgreSQL installed on your machine.
- Python 3.x installed with the required packages listed in `requirements.txt`.

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/SergeiVorobev/db-transfer-solution.git
    cd db-transfer-solution
    ```

2. **Install required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the databases**:
    - Run the `create_databases_and_tables.py` script to create the necessary databases and tables:
    ```bash
    python3 scripts/create_databases_and_tables.py
    ```

4. **Insert sample data into databases**:
    - Run the `insert_sample_data.py` script to populate the DEV and PROD databases with sample data from the JSON files in the `sample_data` directory:
    ```bash
    python3 scripts/insert_sample_data.py
    ```

5. **Transfer and synchronize data from DEV to PROD**:
    - Run the `data_transfer.py` script to transfer and synchronize data from the DEV database to the PROD database:
    ```bash
    python3 scripts/data_transfer.py
    ```

## Configuration

- Ensure the `.env` file is properly set up with the correct PostgreSQL credentials:

```env
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_DEV_NAME=your_dev_db_name
DB_PROD_NAME=your_prod_db_name
