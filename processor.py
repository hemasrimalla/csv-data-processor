"""
processor.py
------------
Core data processing logic for the CSV Data Processor.

This module contains pure business and data processing logic:
- Loading CSV files into Python data structures.
- Cleaning and converting data types safely.
- Filtering and tracking invalid or messy records.
- Calculating statistical summaries and department-level aggregations.

Note: This file contains NO print statements and NO report formatting.
"""

import csv


def load_csv(filepath):
    """
    Read a CSV file using csv.DictReader and return a list of dictionaries.

    Args:
        filepath (str): The path to the CSV file to be loaded.

    Returns:
        list[dict]: A list of row dictionaries mapping headers to cell values.

    Raises:
        FileNotFoundError: If the specified file does not exist at filepath.
    """
    try:
        # newline="" is recommended by the Python csv documentation to prevent blank lines
        with open(filepath, mode="r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: Unable to locate CSV file at '{filepath}'.")


def safe_float(value):
    """
    Safely convert a string or numeric value to a float.

    Args:
        value: The raw value to convert (string, int, float, or None).

    Returns:
        float or None: The parsed float value, or None if the value is missing or invalid.
    """
    if value is None:
        return None
    val_str = str(value).strip()
    if not val_str:
        return None
    try:
        return float(val_str)
    except ValueError:
        return None


def clean_row(row):
    """
    Validate and clean a single employee record.

    Validates that:
    - Required text fields ('name', 'department') are present and non-empty.
    - 'salary' is present, non-empty, and can be converted to a positive float.
    - 'age' is present, non-empty, and can be converted to a positive number.
    - 'years_experience' is present, non-empty, and can be converted to a valid number.

    Args:
        row (dict): A single dictionary representing an employee from the CSV.

    Returns:
        tuple[dict or None, str or None]:
            - If valid: (cleaned_dict, None)
            - If invalid: (None, error_reason)
    """
    # 1. Validate employee name
    name = row.get("name", "").strip() if row.get("name") else ""
    if not name:
        return None, "Missing employee name"

    # 2. Validate department
    dept = row.get("department", "").strip() if row.get("department") else ""
    if not dept:
        return None, "Missing department"

    # 3. Validate salary
    raw_salary = row.get("salary")
    if raw_salary is None or str(raw_salary).strip() == "":
        return None, "Missing salary"
    salary = safe_float(raw_salary)
    if salary is None:
        return None, f"Invalid salary format ('{raw_salary.strip()}')"
    if salary < 0:
        return None, f"Negative salary value ('{raw_salary.strip()}')"

    # 4. Validate age
    raw_age = row.get("age")
    if raw_age is None or str(raw_age).strip() == "":
        return None, "Missing age"
    age = safe_float(raw_age)
    if age is None:
        return None, f"Invalid age format ('{raw_age.strip()}')"
    if age <= 0 or age > 120:
        return None, f"Unrealistic age value ('{raw_age.strip()}')"

    # 5. Validate years of experience
    raw_exp = row.get("years_experience")
    if raw_exp is None or str(raw_exp).strip() == "":
        return None, "Missing years of experience"
    exp = safe_float(raw_exp)
    if exp is None or exp < 0:
        return None, f"Invalid years of experience ('{str(raw_exp).strip()}')"

    # Construct the cleaned record with strongly-typed values
    cleaned = {
        "id": str(row.get("id", "")).strip(),
        "name": name,
        "department": dept,
        "salary": salary,
        "age": age,
        "years_experience": exp,
    }
    return cleaned, None


def process_rows(raw_rows):
    """
    Separate raw CSV rows into valid cleaned records and tracked skipped records.

    Args:
        raw_rows (list[dict]): The raw records loaded from the CSV file.

    Returns:
        tuple[list[dict], list[dict]]:
            - valid_rows: List of properly typed employee dicts.
            - skipped_rows: List of dicts describing skipped rows and the reasons.
    """
    valid_rows = []
    skipped_rows = []

    for index, row in enumerate(raw_rows, start=1):
        cleaned, error = clean_row(row)
        if error:
            skipped_rows.append({
                "row_number": index,
                "id": row.get("id", "N/A"),
                "name": row.get("name", "Unknown"),
                "raw_data": row,
                "reason": error,
            })
        else:
            valid_rows.append(cleaned)

    return valid_rows, skipped_rows


def calculate_statistics(rows, skipped_rows=None):
    """
    Calculate summary and department-level statistics from employee data.

    Accepts either:
    1. Pre-cleaned valid rows with an optional list of skipped_rows.
    2. Raw rows loaded directly from load_csv (will clean and separate automatically).

    Args:
        rows (list[dict]): Valid employee records or raw CSV records.
        skipped_rows (list[dict], optional): List of tracked skipped records.

    Returns:
        dict: A comprehensive dictionary containing:
            - total_records (int): Count of all records (valid + skipped).
            - valid_records (int): Count of valid processed records.
            - skipped_records (int): Count of skipped/invalid records.
            - total_salary (float): Sum of all salaries.
            - average_salary (float): Mean salary across valid employees.
            - average_age (float): Mean age across valid employees.
            - highest_salary (dict): Name, salary, and department of the top earner.
            - lowest_salary (dict): Name, salary, and department of the lowest earner.
            - department_counts (dict): {department: employee_count}.
            - department_average_salaries (dict): {department: average_salary}.
            - department_highest_paid (dict): {department: {"name": ..., "salary": ...}}.
            - skipped_details (list[dict]): Details of skipped rows.
    """
    # Auto-detect if raw uncleaned rows were passed directly
    if skipped_rows is None:
        if rows and any(isinstance(r.get("salary"), str) for r in rows):
            valid_rows, skipped = process_rows(rows)
            skipped_rows = skipped
        else:
            valid_rows = list(rows)
            skipped_rows = []
    else:
        valid_rows = list(rows)

    total_records = len(valid_rows) + len(skipped_rows)
    valid_count = len(valid_rows)
    skipped_count = len(skipped_rows)

    # Handle edge case where no valid rows exist
    if valid_count == 0:
        return {
            "total_records": total_records,
            "valid_records": 0,
            "skipped_records": skipped_count,
            "total_salary": 0.0,
            "average_salary": 0.0,
            "average_age": 0.0,
            "highest_salary": None,
            "lowest_salary": None,
            "department_counts": {},
            "department_average_salaries": {},
            "department_highest_paid": {},
            "skipped_details": skipped_rows,
        }

    # 1. Total salary payout
    total_salary = sum(emp["salary"] for emp in valid_rows)

    # 2. Overall averages
    average_salary = total_salary / valid_count
    average_age = sum(emp["age"] for emp in valid_rows) / valid_count

    # 3. Overall highest and lowest salary earners
    highest_emp = max(valid_rows, key=lambda emp: emp["salary"])
    lowest_emp = min(valid_rows, key=lambda emp: emp["salary"])

    highest_salary = {
        "name": highest_emp["name"],
        "salary": highest_emp["salary"],
        "department": highest_emp["department"],
    }
    lowest_salary = {
        "name": lowest_emp["name"],
        "salary": lowest_emp["salary"],
        "department": lowest_emp["department"],
    }

    # 4. Department-level statistics
    department_groups = {}
    for emp in valid_rows:
        dept = emp["department"]
        if dept not in department_groups:
            department_groups[dept] = []
        department_groups[dept].append(emp)

    department_counts = {}
    department_average_salaries = {}
    department_highest_paid = {}

    for dept, emp_list in department_groups.items():
        dept_count = len(emp_list)
        dept_total_salary = sum(e["salary"] for e in emp_list)
        dept_avg_salary = dept_total_salary / dept_count
        dept_highest_emp = max(emp_list, key=lambda e: e["salary"])

        department_counts[dept] = dept_count
        department_average_salaries[dept] = dept_avg_salary
        department_highest_paid[dept] = {
            "name": dept_highest_emp["name"],
            "salary": dept_highest_emp["salary"],
        }

    return {
        "total_records": total_records,
        "valid_records": valid_count,
        "skipped_records": skipped_count,
        "total_salary": total_salary,
        "average_salary": average_salary,
        "average_age": average_age,
        "highest_salary": highest_salary,
        "lowest_salary": lowest_salary,
        "department_counts": department_counts,
        "department_average_salaries": department_average_salaries,
        "department_highest_paid": department_highest_paid,
        "skipped_details": skipped_rows,
    }
