"""
TSV IMPORT - For tab-separated files
Run this to import your tab-separated employee data
"""
import mysql.connector
import pandas as pd
import os
from mysql.connector import Error

def tsv_import():
    print("=" * 70)
    print("TSV (TAB-SEPARATED) IMPORT TOOL")
    print("=" * 70)
    
    # Find the file
    csv_file = None
    possible_paths = [
        'employee_attrition.csv',
        'hr_attrition_clean (2).csv',
        'data/employee_attrition.csv',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            print(f"Found file: {csv_file}")
            break
    
    if not csv_file:
        print("\nERROR: Could not find CSV file!")
        return
    
    # Read TSV file (tab-separated)
    try:
        print(f"\nReading {csv_file} with tab separator...")
        # Use \t as the separator for tab-separated values
        df = pd.read_csv(csv_file, sep='\t')
        print(f"✅ Read {len(df)} records")
        print(f"Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    print(f"Cleaned columns: {df.columns.tolist()}")
    
    # Check if EmployeeNumber exists
    if 'EmployeeNumber' not in df.columns:
        print("\n⚠️ 'EmployeeNumber' column not found!")
        print("Available columns:", df.columns.tolist())
        return
    
    # Show sample data
    print("\nSample data:")
    print(df[['EmployeeNumber', 'Age', 'Department', 'Attrition']].head())
    
    # Connect to MySQL
    print("\nConnecting to MySQL...")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='employee_attrition',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        print("✅ Connected to MySQL")
    except Error as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Clear table
    print("\nClearing existing data...")
    try:
        cursor.execute("DELETE FROM employees")
        conn.commit()
        print("✅ Cleared existing data")
    except Error as e:
        print(f"⚠️ Could not clear table: {e}")
    
    # Prepare insert query
    insert_query = """
    INSERT INTO employees (
        employee_number, age, daily_rate, department, distance_from_home,
        education, education_field, environment_satisfaction, hourly_rate,
        job_involvement, job_level, job_role, job_satisfaction,
        marital_status, monthly_income, monthly_rate, num_companies_worked,
        percent_salary_hike, performance_rating, relationship_satisfaction,
        stock_option_level, total_working_years, training_times_last_year,
        work_life_balance, years_at_company, years_in_current_role,
        years_since_last_promotion, years_with_curr_manager,
        overtime, gender, business_travel, attrition
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    """
    
    def clean(val):
        """Convert NaN to None for MySQL NULL"""
        if pd.isna(val):
            return None
        return val
    
    # Insert data in batches
    print("\nInserting data...")
    inserted = 0
    errors = 0
    duplicate_errors = 0
    batch_size = 100
    batch = []
    
    # Get unique employee numbers for debugging
    unique_emps = df['EmployeeNumber'].nunique()
    print(f"Unique employee numbers in CSV: {unique_emps}")
    
    for index, row in df.iterrows():
        try:
            employee_num = clean(row.get('EmployeeNumber'))
            
            # Skip if employee number is None or 0
            if employee_num is None or employee_num == 0:
                print(f"  Skipping row {index}: EmployeeNumber is {employee_num}")
                continue
            
            params = (
                employee_num,
                clean(row.get('Age')),
                clean(row.get('DailyRate')),
                clean(row.get('Department')),
                clean(row.get('DistanceFromHome')),
                clean(row.get('Education')),
                clean(row.get('EducationField')),
                clean(row.get('EnvironmentSatisfaction')),
                clean(row.get('HourlyRate')),
                clean(row.get('JobInvolvement')),
                clean(row.get('JobLevel')),
                clean(row.get('JobRole')),
                clean(row.get('JobSatisfaction')),
                clean(row.get('MaritalStatus')),
                clean(row.get('MonthlyIncome')),
                clean(row.get('MonthlyRate')),
                clean(row.get('NumCompaniesWorked')),
                clean(row.get('PercentSalaryHike')),
                clean(row.get('PerformanceRating')),
                clean(row.get('RelationshipSatisfaction')),
                clean(row.get('StockOptionLevel')),
                clean(row.get('TotalWorkingYears')),
                clean(row.get('TrainingTimesLastYear')),
                clean(row.get('WorkLifeBalance')),
                clean(row.get('YearsAtCompany')),
                clean(row.get('YearsInCurrentRole')),
                clean(row.get('YearsSinceLastPromotion')),
                clean(row.get('YearsWithCurrManager')),
                clean(row.get('OverTime')),
                clean(row.get('Gender')),
                clean(row.get('BusinessTravel')),
                clean(row.get('Attrition'))
            )
            
            batch.append(params)
            
            if len(batch) >= batch_size:
                try:
                    cursor.executemany(insert_query, batch)
                    conn.commit()
                    inserted += len(batch)
                    print(f"  Inserted {inserted} records...")
                    batch = []
                except Error as e:
                    if "Duplicate entry" in str(e):
                        duplicate_errors += len(batch)
                        print(f"  Duplicate errors for batch, skipping...")
                        batch = []
                    else:
                        raise e
                
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error at row {index}: {e}")
    
    # Insert remaining
    if batch:
        try:
            cursor.executemany(insert_query, batch)
            conn.commit()
            inserted += len(batch)
        except Error as e:
            if "Duplicate entry" in str(e):
                duplicate_errors += len(batch)
                print(f"  Duplicate errors for final batch, skipping...")
            else:
                print(f"  Error in final batch: {e}")
    
    # Verify
    print("\nVerifying import...")
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    
    print("\n" + "=" * 70)
    print("IMPORT RESULTS")
    print("=" * 70)
    print(f"✅ Records inserted: {inserted}")
    print(f"⚠️ Duplicate entries skipped: {duplicate_errors}")
    print(f"⚠️ Other errors: {errors}")
    print(f"✅ Total in database: {count}")
    
    if count > 0:
        print("\nSample records from database:")
        cursor.execute("SELECT employee_number, age, department, attrition FROM employees LIMIT 5")
        for row in cursor.fetchall():
            print(f"  Employee #{row[0]}, Age: {row[1]}, Dept: {row[2]}, Attrition: {row[3]}")
    else:
        print("\n⚠️ WARNING: No records found in database!")
        
        # Debug: Check CSV data
        print("\nDebug - First 5 rows of CSV:")
        print(df[['EmployeeNumber', 'Age', 'Department']].head())
    
    print("=" * 70)
    
    cursor.close()
    conn.close()
    print("\n✅ Import complete!")

if __name__ == "__main__":
    tsv_import()
    