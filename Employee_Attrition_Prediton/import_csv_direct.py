"""
DIRECT CSV IMPORT - Uses raw MySQL connection
Run this to import your CSV data directly
"""
import mysql.connector
import pandas as pd
import os
from mysql.connector import Error

def direct_import():
    print("=" * 70)
    print("DIRECT CSV IMPORT TOOL")
    print("=" * 70)
    
    # Find CSV file
    csv_file = None
    possible_paths = [
        'employee_attrition.csv',
        'hr_attrition_clean (2).csv',
        'data/employee_attrition.csv',
        '../employee_attrition.csv',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            print(f"Found CSV: {csv_file}")
            break
    
    if not csv_file:
        print("\nERROR: Could not find CSV file!")
        print("Please make sure your CSV is in the project folder")
        print("Current directory:", os.getcwd())
        print("Files in directory:", os.listdir('.'))
        return
    
    # Read CSV
    try:
        print(f"\nReading {csv_file}...")
        df = pd.read_csv(csv_file)
        print(f"✅ Read {len(df)} records")
        print(f"Columns: {df.columns.tolist()[:5]}...")  # Show first 5 columns
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
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
        print("\nMake sure:")
        print("1. XAMPP is running")
        print("2. MySQL service is started")
        print("3. Database 'employee_attrition' exists")
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
    
    # Insert data in batches
    print("\nInserting data...")
    inserted = 0
    errors = 0
    batch_size = 100
    batch = []
    
    def clean(val):
        """Convert NaN to None for MySQL NULL"""
        if pd.isna(val):
            return None
        return val
    
    for index, row in df.iterrows():
        try:
            # Map column names to match your CSV
            # Adjust these if your column names are different
            params = (
                clean(row.get('EmployeeNumber') or row.get('EmployeeNumber')),
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
                cursor.executemany(insert_query, batch)
                conn.commit()
                inserted += len(batch)
                print(f"  Inserted {inserted} records...")
                batch = []
                
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"  Error at row {index}: {e}")
    
    # Insert remaining
    if batch:
        cursor.executemany(insert_query, batch)
        conn.commit()
        inserted += len(batch)
    
    # Verify
    print("\nVerifying import...")
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    
    print("\n" + "=" * 70)
    print("IMPORT RESULTS")
    print("=" * 70)
    print(f"✅ Records inserted: {inserted}")
    print(f"⚠️ Errors: {errors}")
    print(f"✅ Total in database: {count}")
    
    if count > 0:
        print("\nSample records:")
        cursor.execute("SELECT employee_number, age, department, attrition FROM employees LIMIT 3")
        for row in cursor.fetchall():
            print(f"  Employee #{row[0]}, Age: {row[1]}, Dept: {row[2]}, Attrition: {row[3]}")
    else:
        print("\n⚠️ WARNING: No records found in database!")
        print("Please check if the table structure matches your CSV columns")
    
    print("=" * 70)
    
    cursor.close()
    conn.close()
    print("\n✅ Import complete!")

if __name__ == "__main__":
    direct_import()
    