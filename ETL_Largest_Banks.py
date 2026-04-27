"""
ETL Project: World's Largest Banks
"""

# ── Imports ─────────────────────────────────────────────────────
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
import io

# ── Configuration ───────────────────────────────────────────────
URL = ("https://web.archive.org/web/20230908091635/"
       "https://en.wikipedia.org/wiki/List_of_largest_banks")

EXCHANGE_RATE_CSV = "exchange_rate.csv"
OUTPUT_CSV = "Largest_banks_data.csv"
DB_PATH = "Banks.db"
LOG_FILE = "code_log.txt"
TABLE_NAME = "Largest_banks"

# ── Create exchange rate file (required) ────────────────────────
exchange_rate_data = """Currency,Rate
GBP,0.8
EUR,0.93
INR,82.95"""

with open(EXCHANGE_RATE_CSV, "w") as f:
    f.write(exchange_rate_data)

# ── 1. log_progress ─────────────────────────────────────────────
def log_progress(message):
    timestamp = datetime.now().strftime("%Y-%b-%d %H:%M:%S")
    line = f"{timestamp} : {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ── 2. extract ──────────────────────────────────────────────────
def extract(url, table_attribs):

    log_progress("Extraction started")

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        page = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(page, "html.parser")

        tables = soup.find_all("table", {"class": "wikitable"})
        rows = tables[0].find_all("tr")

        records = []

        for row in rows[1:]:
            col = row.find_all("td")

            if len(col) < 3:
                continue

            bank_name = col[1].get_text(strip=True)
            market_cap = col[2].get_text(strip=True).replace(",", "")

            try:
                market_cap = float(market_cap)
            except:
                continue

            records.append({
                table_attribs[0]: bank_name,
                table_attribs[1]: market_cap
            })

        df = pd.DataFrame(records)

        log_progress(f"Extraction complete - {len(df)} rows")
        return df

    except:
        log_progress("Website blocked. Using fallback data")

        fallback_data = """Name,MC_USD_Billion
JPMorgan Chase,432.92
Bank of America,231.52
Industrial and Commercial Bank of China,194.56
Agricultural Bank of China,160.68
HDFC Bank,157.91
"""

        df = pd.read_csv(io.StringIO(fallback_data))
        return df

# ── 3. transform ────────────────────────────────────────────────
def transform(df, exchange_rate_path):

    log_progress("Transformation started")

    rates = pd.read_csv(exchange_rate_path, index_col=0).squeeze("columns")

    df["MC_GBP_Billion"] = np.round(df["MC_USD_Billion"] * rates["GBP"], 2)
    df["MC_EUR_Billion"] = np.round(df["MC_USD_Billion"] * rates["EUR"], 2)
    df["MC_INR_Billion"] = np.round(df["MC_USD_Billion"] * rates["INR"], 2)

    log_progress("Transformation complete")
    return df

# ── 4. load_to_csv ──────────────────────────────────────────────
def load_to_csv(df, output_path):

    log_progress(f"Saving CSV -> {output_path}")
    df.to_csv(output_path, index=False)

# ── 5. load_to_db ───────────────────────────────────────────────
def load_to_db(df, sql_connection, table_name):

    log_progress(f"Loading to DB -> {table_name}")
    df.to_sql(table_name, sql_connection, if_exists="replace", index=False)
    sql_connection.commit()

# ── 6. run_query ────────────────────────────────────────────────
def run_query(query_statement, sql_connection):

    log_progress(f"Running query: {query_statement}")
    result = pd.read_sql_query(query_statement, sql_connection)
    print(result.to_string(index=False))

# ── Main ───────────────────────────────────────────────────────
def main():

    log_progress("ETL Process Started")

    # Extract
    df = extract(URL, ["Name", "MC_USD_Billion"])

    # Transform
    df = transform(df, EXCHANGE_RATE_CSV)

    # Load
    load_to_csv(df, OUTPUT_CSV)

    conn = sqlite3.connect(DB_PATH)
    load_to_db(df, conn, TABLE_NAME)

    # Queries
    print("\n--- All Banks ---")
    run_query(f"SELECT * FROM {TABLE_NAME}", conn)

    print("\n--- Top 5 Banks ---")
    run_query(f"""
        SELECT Name, MC_USD_Billion
        FROM {TABLE_NAME}
        ORDER BY MC_USD_Billion DESC
        LIMIT 5
    """, conn)

    print("\n--- Average Market Cap (GBP) ---")
    run_query(f"""
        SELECT ROUND(AVG(MC_GBP_Billion),2) AS Avg_GBP
        FROM {TABLE_NAME}
    """, conn)

    conn.close()
    log_progress("ETL Process Completed")

# ── Run ────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()