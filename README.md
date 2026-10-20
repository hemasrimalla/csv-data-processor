# CSV Data Processor (Task 20, Level 1)

A beginner-friendly, zero-dependency Python project that reads tabular employee data from a CSV file, cleans and validates records, handles messy/missing data gracefully, and computes key organizational statistics (aggregates, department breakdowns, and error tracking).

Built strictly using **Python's standard library** (`csv` module) without external dependencies like pandas.

---

## Project Structure

```text
csv-data-processor/
├── data/
│   └── employees.csv       # Input dataset with 24 employee records (including 3 messy rows)
├── processor.py            # Pure business & data-processing logic (no prints or formatting)
├── main.py                 # Application entry point: CLI orchestration, reporting, and file writing
├── report.txt              # Automatically generated text summary report
└── README.md               # Project documentation and interview Q&A
```

---

## Key Features

1. **Pure Python Standard Library**:
   - Uses built-in `csv.DictReader` to parse tabular data into intuitive dictionary objects.
   - Zero external libraries or package installations required.

2. **Defensive Data Cleaning & Error Handling**:
   - Custom `safe_float()` helper handles type conversions cleanly without crashing.
   - Identifies and tracks skipped records with human-readable error reasons (missing values, unparseable numbers).

3. **Separation of Concerns**:
   - **`processor.py`**: Pure calculation and data-handling logic. Returns structured data (`dict`, `list`).
   - **`main.py`**: Handles user I/O, console display, string alignment with f-strings, and file saving.

4. **Comprehensive Reporting**:
   - Overall metrics: total records, valid vs. skipped counts, total salary payout, average salary, and average age.
   - Overall highest-paid and lowest-paid employees.
   - Department breakdown: headcount, average salary, and highest earner per department.
   - Detailed audit table listing all skipped rows and their specific failure reasons.

---

## How to Run

Ensure Python 3.8+ is installed on your machine.

1. Open a terminal or command prompt.
2. Navigate to the project directory:
   ```bash
   cd csv-data-processor
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Check the generated `report.txt` file in the same directory.

---

## Sample Output

When running `python main.py`, the console and `report.txt` display:

```text
================================================================================
                         CSV DATA PROCESSOR: SUMMARY REPORT
================================================================================

1. OVERALL METRICS
--------------------------------------------------------------------------------
Total Records in File:              24
  - Valid Records Processed:        21
  - Skipped / Invalid Records:      3

Total Salary Payout:                $1,787,000.00
Average Annual Salary:              $85,095.24
Average Employee Age:               34.5 years

Highest Salary:                     $128,000.00 (Sarah Connor - IT)
Lowest Salary:                      $58,000.00 (Hannah Abbott - HR)

2. DEPARTMENT BREAKDOWN
--------------------------------------------------------------------------------
Department        Count       Average Salary   Highest Paid Employee           
--------------------------------------------------------------------------------
Finance               4           $93,250.00   Victor Vance ($102,000.00)      
HR                    4           $64,000.00   Toby Flenderson ($69,000.00)    
IT                    6          $101,500.00   Sarah Connor ($128,000.00)      
Marketing             4           $74,000.00   Uma Thurman ($85,000.00)        
Sales                 3           $84,333.33   Michael Scott ($92,000.00)      

3. SKIPPED / INVALID RECORDS (3)
--------------------------------------------------------------------------------
Row #   ID       Name                   Reason                                  
--------------------------------------------------------------------------------
4       104      Diana Prince           Missing salary                          
12      112      Laura Croft            Invalid salary format ('abc')           
18      118      Ryan Howard            Missing age                             
================================================================================
```

---

## Concepts Learned

### 1. The `csv` Module
Python's standard library `csv` module provides robust primitives for reading and writing delimited text files, managing escaping, delimiter delimiters (commas, tabs), and quotation marks according to RFC 4180. Using `with open(..., newline="")` prevents cross-platform newline translation issues.

### 2. `csv.DictReader` vs. `csv.reader`
- `csv.reader` returns each row as a plain `list` of strings accessed by index (e.g., `row[3]`), which is brittle if column order changes.
- `csv.DictReader` reads the first row as field names and parses subsequent rows into Python dictionaries (e.g., `row["salary"]`). This improves readability, eliminates off-by-one index bugs, and allows non-breaking column order adjustments.

### 3. Defensive Error Handling & Type Casting
CSV data is read purely as strings. Trying to immediately cast fields with `float(row["salary"])` causes unhandled exceptions (`ValueError` or `TypeError`) when dirty data is encountered. Implementing helper functions like `safe_float()` alongside `try...except` blocks ensures that bad data is isolated without terminating the entire pipeline.

### 4. Separation of Logic and Output
Decoupling calculation logic (`processor.py`) from presentation logic (`main.py`) is a fundamental software engineering principle:
- **Testability**: Pure functions taking inputs and returning outputs can be easily tested without intercepting standard output (`sys.stdout`).
- **Reusability**: The statistical engine can be reused in a web API, desktop GUI, or batch pipeline without modification.
- **Maintainability**: Changing how the report is formatted (e.g., changing currency symbols or column padding) does not touch the math engine.

---

## Interview Questions & Answers

### 1. What is CSV?
**Answer:**  
CSV stands for **Comma-Separated Values**. It is a plain-text file format used to store tabular data (numbers and text) in a structured, lightweight format.
- Each line in a CSV file corresponds to one record (row).
- Each record consists of one or more fields separated by a delimiter, most commonly a comma (`,`), but sometimes semicolons (`;`) or tabs (`\t`).
- The first line typically serves as a header row defining column names.
- Because it is plain text, CSV is platform-independent, human-readable, and supported by almost all spreadsheet programs, database systems, and programming languages.

### 2. How can Python read CSV files?
**Answer:**  
Python provides multiple ways to read CSV files, depending on project requirements:
1. **Built-in `csv.reader`**: Reads records line-by-line as lists of strings. Useful for simple files where memory overhead must be minimal.
2. **Built-in `csv.DictReader`**: Reads rows as dictionaries mapping header names to cell strings. Highly recommended for readability and maintainability when column names are present.
3. **Manual File Parsing (`open()` and `.split(','`)**: Possible for trivial cases, but strongly discouraged because it fails to handle edge cases like commas inside quoted strings, escaped quotes, and multiline cells.
4. **Third-Party Libraries (`pandas.read_csv()`, `polars.read_csv()`)**: Excellent for large datasets, data science, and complex statistical analysis, but adds external dependencies.

### 3. How would you handle missing values in a CSV?
**Answer:**  
Handling missing values requires a combination of detection, business validation, and imputation or exclusion:
1. **Detection & Safe Parsing**: Strip whitespace and check for empty strings (`""`), `None`, or placeholder strings (such as `"N/A"`, `"null"`, `"-"`). Use defensive parsing functions (`try...except ValueError`) rather than direct type casting.
2. **Exclusion (Filtering)**: If the missing field is mandatory (e.g., an employee's salary or an account ID), filter the record out, log the skipped row with the line number and reason, and continue processing valid rows.
3. **Imputation (Default Values)**: If appropriate for the business domain, replace missing numeric values with defaults such as the column mean, median, or zero; or fill missing text values with `"Unknown"`.
4. **Flagging**: Maintain an audit trail of modified or dropped records so data quality issues can be reported back to the data provider.
