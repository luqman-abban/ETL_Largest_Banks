#  ETL Pipeline: World’s Largest Banks

##  Project Overview

This project demonstrates a complete **ETL (Extract, Transform, Load) pipeline** using Python to collect and process data on the **world’s largest banks by market capitalization**.

The pipeline extracts data from a web source, transforms it into a usable format, and loads it into both a CSV file and a SQLite database for analysis.

---

##  Technologies Used

* Python
* Pandas
* BeautifulSoup (Web Scraping)
* NumPy


---

##  ETL Process

###  Extract

* Scrapes bank data (Name, Market Cap) from an archived Wikipedia page
* Includes fallback handling in case of network failure

###  Transform

* Cleans and converts market cap values to numeric format
* Converts USD values into:

  * GBP
  * EUR
  * INR

###  Load

* Saves processed data to:

  * CSV file (`Largest_banks_data.csv`)
  * SQLite database (`Banks.db`)

###  Query

* Executes SQL queries to:

  * View all banks
  * Identify top banks by market cap
  * Calculate average values

---

##  Project Files

```bash
banks_project.py        # Main ETL script
exchange_rate.csv       # Currency rates
Largest_banks_data.csv  # Output dataset
Banks.db                # Database file
code_log.txt            # Execution logs
README.md               # Documentation
```

---

##  How to Run

```bash
pip install pandas numpy requests beautifulsoup4
python banks_project.py
```

---

##  Key Features

* End-to-end ETL pipeline
* Data cleaning and transformation
* Multi-currency conversion
* Database storage and SQL querying
* Logging system for tracking execution

---

##  Notes

* The script uses fallback data if the website is unavailable
* Exchange rates are stored locally for consistency


---

## 👤 Author

Luqman Abban

