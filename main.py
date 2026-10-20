"""
main.py
-------
Entry point for the CSV Data Processor project.

Responsibilities:
- Reads configuration and file paths.
- Invokes data loading, validation, and analytics from processor.py.
- Generates a cleanly aligned, professional text report using f-strings.
- Displays the report in the console.
- Saves the identical report to 'report.txt'.
"""

import os
import sys

from processor import calculate_statistics, load_csv, process_rows


def format_currency(amount, symbol="$"):
    """
    Format a numeric amount into a readable currency string.
    Example: 128000.0 -> $128,000.00 (or ₹128,000.00 if symbol='₹')

    Args:
        amount (float): Numeric value to format.
        symbol (str): Currency symbol prefix. Defaults to '$'.

    Returns:
        str: Formatted currency string.
    """
    if amount is None:
        return "N/A"
    return f"{symbol}{amount:,.2f}"


def build_report_text(stats, currency_symbol="$"):
    """
    Construct a formatted, multi-section summary report.

    Args:
        stats (dict): Dictionary of calculated statistics from calculate_statistics().
        currency_symbol (str): Symbol to prepend to currency figures.

    Returns:
        str: Cleanly aligned multi-line report string.
    """
    lines = []
    divider_double = "=" * 80
    divider_single = "-" * 80

    # Header
    lines.append(divider_double)
    lines.append("                         CSV DATA PROCESSOR: SUMMARY REPORT")
    lines.append(divider_double)
    lines.append("")

    # Section 1: Overall Summary
    lines.append("1. OVERALL METRICS")
    lines.append(divider_single)
    lines.append(f"{'Total Records in File:':<35} {stats['total_records']}")
    lines.append(f"{'  - Valid Records Processed:':<35} {stats['valid_records']}")
    lines.append(f"{'  - Skipped / Invalid Records:':<35} {stats['skipped_records']}")
    lines.append("")
    lines.append(f"{'Total Salary Payout:':<35} {format_currency(stats['total_salary'], currency_symbol)}")
    lines.append(f"{'Average Annual Salary:':<35} {format_currency(stats['average_salary'], currency_symbol)}")
    lines.append(f"{'Average Employee Age:':<35} {stats['average_age']:.1f} years")
    lines.append("")

    if stats["highest_salary"]:
        h_name = stats["highest_salary"]["name"]
        h_dept = stats["highest_salary"]["department"]
        h_sal = format_currency(stats["highest_salary"]["salary"], currency_symbol)
        lines.append(f"{'Highest Salary:':<35} {h_sal} ({h_name} - {h_dept})")
    else:
        lines.append(f"{'Highest Salary:':<35} None")

    if stats["lowest_salary"]:
        l_name = stats["lowest_salary"]["name"]
        l_dept = stats["lowest_salary"]["department"]
        l_sal = format_currency(stats["lowest_salary"]["salary"], currency_symbol)
        lines.append(f"{'Lowest Salary:':<35} {l_sal} ({l_name} - {l_dept})")
    else:
        lines.append(f"{'Lowest Salary:':<35} None")

    lines.append("")

    # Section 2: Department-Level Breakdown
    lines.append("2. DEPARTMENT BREAKDOWN")
    lines.append(divider_single)
    header_dept = f"{'Department':<15} {'Count':>7}   {'Average Salary':>18}   {'Highest Paid Employee':<32}"
    lines.append(header_dept)
    lines.append(divider_single)

    dept_counts = stats.get("department_counts", {})
    dept_avgs = stats.get("department_average_salaries", {})
    dept_tops = stats.get("department_highest_paid", {})

    # Sort departments alphabetically for a predictable, clean table
    for dept in sorted(dept_counts.keys()):
        count = dept_counts[dept]
        avg_sal = format_currency(dept_avgs.get(dept, 0.0), currency_symbol)
        top_info = dept_tops.get(dept, {})
        top_emp_str = f"{top_info.get('name', 'N/A')} ({format_currency(top_info.get('salary', 0.0), currency_symbol)})"
        lines.append(f"{dept:<15} {count:>7}   {avg_sal:>18}   {top_emp_str:<32}")

    lines.append("")

    # Section 3: Skipped / Invalid Rows Section
    skipped_records = stats.get("skipped_details", [])
    lines.append(f"3. SKIPPED / INVALID RECORDS ({len(skipped_records)})")
    lines.append(divider_single)

    if not skipped_records:
        lines.append("All rows were processed successfully. No invalid records found.")
    else:
        header_skipped = f"{'Row #':<7} {'ID':<8} {'Name':<22} {'Reason':<40}"
        lines.append(header_skipped)
        lines.append(divider_single)
        for item in skipped_records:
            row_num = str(item.get("row_number", "N/A"))
            emp_id = str(item.get("id", "N/A"))
            name = str(item.get("name", "Unknown"))
            reason = str(item.get("reason", "Unknown error"))
            lines.append(f"{row_num:<7} {emp_id:<8} {name:<22} {reason:<40}")

    lines.append(divider_double)
    return "\n".join(lines)


def main():
    """Main execution function to run the data processor and output reports."""
    # Determine directory paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_filepath = os.path.join(base_dir, "data", "employees.csv")
    report_filepath = os.path.join(base_dir, "report.txt")

    print(f"Loading data from: {data_filepath}")

    try:
        raw_rows = load_csv(data_filepath)
    except FileNotFoundError as err:
        print(f"\n[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    # Process and separate valid rows from skipped/invalid rows
    valid_rows, skipped_rows = process_rows(raw_rows)

    # Compute comprehensive statistics
    stats = calculate_statistics(valid_rows, skipped_rows=skipped_rows)

    # Format the report text
    report_text = build_report_text(stats, currency_symbol="$")

    # 1. Print report to console
    print("\n" + report_text + "\n")

    # 2. Save report to report.txt
    try:
        with open(report_filepath, mode="w", encoding="utf-8") as report_file:
            report_file.write(report_text + "\n")
        print(f"[SUCCESS] Report successfully generated and saved to: {report_filepath}")
    except OSError as err:
        print(f"[ERROR] Could not write report to file: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
