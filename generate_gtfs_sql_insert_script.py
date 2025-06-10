# generate_gtfs_sql_insert_script.py

import csv
import os

DATA_DIR = "./backend/data/gtfs"
OUTPUT_FILE = "gtfs_insert_statements.sql.txt"

def escape_value(value):
    if value == "":
        return "NULL"
    if value.upper() == "NULL":
        return "NULL"
    escaped = value.replace("'", "''")
    # Escape single quotes for SQL
    return f"'{escaped}'"

def process_file(file_path, table_name):
    inserts = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            columns = ', '.join(row.keys())
            values = ', '.join(escape_value(value) for value in row.values())
            insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            inserts.append(insert_stmt)
    return inserts

def main():
    all_inserts = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            table_name = os.path.splitext(filename)[0]  # e.g. routes.txt → routes
            file_path = os.path.join(DATA_DIR, filename)
            print(f"Processing {filename} → table {table_name}")
            try:
                inserts = process_file(file_path, table_name)
                all_inserts.extend(inserts)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Write all insert statements to a .sql.txt file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        for stmt in all_inserts:
            out_file.write(stmt + "\n")

    print(f"\n✅ Done. SQL statements written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
